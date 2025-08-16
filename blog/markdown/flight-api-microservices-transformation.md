---
title: "From Monolith to Microservices: How We Rebuilt Our Flight API and Cut Response Time by 70%"
description: "The complete story of transforming a monolithic flight booking system into three specialized microservices, reducing API calls by 60% and DB operations by 80%."
keywords: ["microservices", "flight-api", "system-architecture", "performance-optimization", "sharetrip", "redis-cache", "rabbitmq", "api-gateway"]
date: "2024-12-19"
readTime: "14 min read"
category: "Architecture"
slug: "flight-api-microservices-transformation"
---

# From Monolith to Microservices: How We Rebuilt Our Flight API and Cut Response Time by 70%

## TL;DR

Our team at ShareTrip completely transformed a monolithic flight booking system into a three-layer microservices architecture. The result? **70% faster response times**, **60% fewer API calls**, and **80% reduction in database operations**. Here's the complete story of how we went from a single overwhelming codebase to a scalable, maintainable system that handles massive traffic with ease.

---

## The Monster We Had to Tame

Picture this: It's 3 AM, and our flight booking system is crawling under peak traffic. Users are complaining about timeouts, the database is screaming for mercy, and our single `Flight-Private` repository is doing... well, everything.

This monolithic beast was handling:
- **Authentication and rate limiting** 🔐
- **Business logic and decision making** 🧠
- **Database operations** 💾
- **Third-party API calls** 🌐
- **Cache management** ⚡
- **Response formatting** 📝
- **Message queue operations** 📨

One repository. One deployment. One massive headache.

The wake-up call came during a flash sale when our system buckled under 10x normal traffic. Response times shot up to 15+ seconds, and we were burning through our third-party API quotas like there was no tomorrow.

**The team knew we had to act fast.**

## The Architecture Revolution: Enter the Three Musketeers

After weeks of planning and heated architectural discussions, we designed a three-layer microservices approach that would change everything:

### Layer 1: B2C-Router - The Smart Gateway
**Role**: Authentication, API rate limiting, and intelligent routing

```typescript
// Before: Everything mixed together
app.post('/flight-search', async (req, res) => {
  // Auth logic mixed with business logic
  if (!validateToken(req.headers.authorization)) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  // Rate limiting mixed with search logic
  if (await checkRateLimit(req.user.id)) {
    return res.status(429).json({ error: 'Too many requests' });
  }
  
  // Business logic starts here...
  const searchResults = await searchFlights(req.body);
  // ... and continues for 200+ lines
});

// After: Clean separation in B2C-Router
app.post('/flight-search', [
  authenticateUser,
  rateLimitMiddleware,
  routeToFlightService
], async (req, res) => {
  // Clean routing logic only
  const response = await forwardToB2CFlight(req);
  res.json(response);
});
```

### Layer 2: B2C-Flight - The Brain
**Role**: Business logic, database operations, cache management, and queue coordination

```typescript
// The intelligent orchestrator
class FlightSearchService {
  async searchFlights(searchParams: FlightSearchDto): Promise<FlightResponse> {
    // 1. Check cache first
    const cachedResults = await this.cacheService.get(searchParams);
    if (cachedResults) {
      return this.formatCachedResponse(cachedResults);
    }
    
    // 2. Prepare search strategy
    const searchStrategy = await this.determineSearchStrategy(searchParams);
    
    // 3. Queue the request to Flight-Engine
    const queueMessage = this.buildEngineMessage(searchParams, searchStrategy);
    await this.queueService.publish('flight-search-queue', queueMessage);
    
    // 4. Wait for processed results
    const engineResponse = await this.waitForEngineResponse(queueMessage.id);
    
    // 5. Apply business logic and save to DB
    const processedResults = await this.applyBusinessRules(engineResponse);
    await this.saveSearchResults(processedResults);
    
    // 6. Update cache for future requests
    await this.cacheService.set(searchParams, processedResults);
    
    return processedResults;
  }
}
```

### Layer 3: Flight-Engine - The Dumb Parser
**Role**: Third-party API communication and response parsing

```typescript
// The focused worker
class FlightEngineService {
  async processSearchRequest(message: QueueMessage): Promise<void> {
    try {
      // 1. Build API request from queue message
      const apiRequest = this.buildThirdPartyRequest(message.payload);
      
      // 2. Make the actual API call
      const rawResponse = await this.thirdPartyApiClient.search(apiRequest);
      
      // 3. Parse into standardized DTOs
      const parsedFlights = this.parseFlightResponse(rawResponse);
      
      // 4. Cache the parsed response
      await this.cacheService.setEngineCache(message.searchId, parsedFlights);
      
      // 5. Send back to B2C-Flight
      await this.notifySearchComplete(message.searchId, parsedFlights);
      
    } catch (error) {
      await this.handleEngineError(message, error);
    }
  }
  
  // No database operations, no business logic - just pure parsing
  private parseFlightResponse(rawData: any): FlightDto[] {
    return rawData.flights.map(flight => ({
      flightNumber: flight.flight_number,
      airline: flight.airline_code,
      departure: this.parseDateTime(flight.departure_time),
      arrival: this.parseDateTime(flight.arrival_time),
      price: this.parsePrice(flight.pricing),
      // ... clean, typed parsing
    }));
  }
}
```

## The Implementation Journey: Blood, Sweat, and Code

### Phase 1: The Great Extraction
We started by identifying and extracting the authentication and routing logic into B2C-Router. This was like performing surgery on a beating heart - the system had to keep running while we carved out pieces.

```typescript
// Migration strategy: Gradual extraction
const routerConfig = {
  routes: [
    {
      path: '/flight-search',
      method: 'POST',
      destination: process.env.B2C_FLIGHT_URL,
      rateLimit: { windowMs: 60000, max: 100 },
      auth: 'required'
    }
  ]
};
```

### Phase 2: The Brain Surgery
Next came the most complex part - splitting the business logic from the API parsing. We had to:

1. **Identify pure business logic** vs. API-specific code
2. **Design the message queue contracts** between services
3. **Implement graceful fallbacks** for when services were unavailable

```typescript
// Queue message contract design
interface FlightSearchMessage {
  id: string;
  searchParams: FlightSearchDto;
  strategy: SearchStrategy;
  priority: 'high' | 'normal' | 'low';
  timeout: number;
  callback: {
    service: 'b2c-flight';
    endpoint: '/search-complete';
  };
}
```

### Phase 3: The Parser Liberation
Finally, we extracted all third-party API logic into Flight-Engine. This service became beautifully simple - it only cared about talking to external APIs and parsing responses.

```typescript
// Clean separation of concerns
class AirlineApiAdapter {
  async search(params: SearchParams): Promise<ParsedFlightData> {
    const response = await this.httpClient.post('/search', params);
    return this.responseParser.parse(response.data);
  }
}
```

## The Moment of Truth: Results That Blew Our Minds

After three months of development and careful migration, we flipped the switch. The results were beyond our wildest expectations:

### Performance Metrics That Speak Volumes

| Metric | Before (Monolith) | After (Microservices) | Improvement |
|--------|------------------|----------------------|-------------|
| **Average Response Time** | 8.5 seconds | 2.1 seconds | **70% faster** |
| **Third-party API Calls** | 450/minute | 180/minute | **60% reduction** |
| **Database Queries** | 1,200/minute | 240/minute | **80% reduction** |
| **Cache Hit Rate** | 35% | 78% | **123% improvement** |
| **System Uptime** | 97.2% | 99.7% | **2.5% improvement** |
| **Concurrent Users Supported** | 500 | 2,000+ | **300% increase** |

### Real-World Impact

**The flash sale that broke us before?** We handled it with flying colors (pun intended). Peak traffic of 15,000 concurrent users, and our system didn't even break a sweat.

**Customer satisfaction scores** jumped from 3.2/5 to 4.6/5, with users specifically praising the "lightning-fast search results."

**Our infrastructure costs** actually went down by 25% despite handling 4x more traffic, thanks to efficient resource utilization across microservices.

## The Technical Deep Dive: How Each Layer Excels

### B2C-Router: The Gatekeeper's Wisdom
```typescript
// Intelligent rate limiting based on user behavior
class SmartRateLimiter {
  async checkLimit(userId: string, endpoint: string): Promise<boolean> {
    const userTier = await this.getUserTier(userId);
    const limits = this.getLimitsForTier(userTier);
    
    // Different limits for different user types
    return await this.redis.checkAndIncrement(
      `${userId}:${endpoint}`, 
      limits.requests, 
      limits.windowMs
    );
  }
}
```

### B2C-Flight: The Orchestration Maestro
```typescript
// Intelligent caching strategy
class FlightCacheManager {
  async getCachedResults(searchParams: FlightSearchDto): Promise<FlightResponse | null> {
    // Multi-layer caching strategy
    const cacheKey = this.generateCacheKey(searchParams);
    
    // L1: In-memory cache (fastest)
    let cached = await this.memoryCache.get(cacheKey);
    if (cached) return cached;
    
    // L2: Redis cache (fast)
    cached = await this.redisCache.get(cacheKey);
    if (cached) {
      await this.memoryCache.set(cacheKey, cached, 300); // 5 min
      return cached;
    }
    
    return null;
  }
}
```

### Flight-Engine: The Parsing Perfectionist
```typescript
// Robust error handling and retry logic
class ThirdPartyApiClient {
  async makeRequest(config: ApiConfig): Promise<ParsedResponse> {
    const maxRetries = 3;
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const response = await this.httpClient.request(config);
        return this.parseResponse(response);
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries) {
          await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
        }
      }
    }
    
    throw new ApiError(`Failed after ${maxRetries} attempts: ${lastError.message}`);
  }
}
```

## Lessons Learned: The Wisdom We Gained

### 1. **Microservices Aren't Magic - They're Strategy**
The biggest lesson? Microservices solved our specific problems because we understood what those problems were. Don't break apart a monolith just because it's trendy - do it because it serves your architecture goals.

### 2. **Queue-Based Communication is a Game Changer**
Using RabbitMQ between B2C-Flight and Flight-Engine eliminated the tight coupling that was killing our performance. Async processing meant we could handle traffic spikes without everything grinding to a halt.

### 3. **Cache Everything, But Cache Smart**
Our multi-layer caching strategy (memory → Redis → database) reduced our database load by 80%. But the key was understanding what to cache and for how long.

### 4. **Monitoring is Non-Negotiable**
With three services, we needed three times the monitoring. We implemented distributed tracing to follow requests across all services - this saved us countless debugging hours.

### 5. **Team Ownership Creates Better Code**
Each team took ownership of one service. The B2C-Router team became authentication experts, the B2C-Flight team mastered business logic, and the Flight-Engine team perfected API integrations. Specialization led to excellence.

## The Road Ahead: What's Next in Our Architecture Journey

### Immediate Improvements (Next 3 Months)
- **GraphQL Federation** to give frontend teams more flexibility
- **Circuit breakers** for even better resilience
- **Auto-scaling** based on queue depth and response times

### Long-term Vision (Next Year)
- **Event sourcing** for better audit trails and debugging
- **CQRS pattern** to separate read and write operations
- **Machine learning** for intelligent caching and request routing

### The Metrics We're Chasing
- **Sub-1-second response times** for cached results
- **99.9% uptime** across all services
- **Support for 10,000+ concurrent users** during peak seasons

## Join the Conversation

This transformation wasn't just about code - it was about changing how our entire team thinks about system design. We went from "how do we fix this?" to "how do we build this right?"

**What's your experience with microservices migrations?** Have you faced similar challenges with monolithic systems? I'd love to hear your stories and lessons learned.

**Connect with me on [LinkedIn](https://linkedin.com/in/mahabubarafat)** - I'm always excited to discuss system architecture, performance optimization, and the real-world challenges of building scalable applications.

---

*Building great software is a team sport. This transformation was possible because of an incredible team of developers, architects, and DevOps engineers who believed in the vision and executed flawlessly. Here's to building systems that don't just work - they excel.*
