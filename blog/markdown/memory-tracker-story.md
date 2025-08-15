---
title: "How I Built a Custom Memory Tracker That Saved Our Production API"
description: "The story of how a custom memory profiling package solved a company-wide production mystery that had everyone stumped. From heap crashes to the root cause."
keywords: ["Node.js", "Memory Management", "NestJS", "Production Debugging", "Memory Leaks", "ShareTrip", "NPM Package"]
date: "2025-01-16"
readTime: "12 min read"
category: "Real Story"
slug: "memory-tracker-production-story"
---

# How I Built a Custom Memory Tracker That Saved Our Production API

**TL;DR:** Our production API kept crashing with "JavaScript heap out of memory" errors. The entire company was hunting for the bug - leads, seniors, DevOps - nobody could find it. So I built a custom memory tracking package that pinpointed the exact function causing the leak. Turns out, a missing `bookingCode` was returning entire database tables. Here's the whole story.

## The Crisis: When Production Goes Down and Nobody Knows Why

Picture this: It's a regular Tuesday morning, and suddenly our production API starts throwing `JavaScript heap out of memory` errors. The app restarts, runs fine for a while, then crashes again. Rinse and repeat.

**The Response Team:**
- All team leads: ✅ Mobilized
- Senior developers: ✅ On the case  
- DevOps team: ✅ Investigating
- Monitoring dashboards: ✅ Showing nothing useful
- Root cause: ❌ Nowhere to be found

> **The Pressure:** This wasn't just any bug. ShareTrip's booking API was unstable, affecting real customers and real revenue. The clock was ticking.

## The Problem: Memory Leaks Are Invisible Enemies

Memory leaks in Node.js are particularly nasty because:

- **They're silent killers** - No immediate symptoms until it's too late
- **Traditional monitoring misses them** - CPU and response time look normal
- **They compound over time** - What starts small becomes catastrophic
- **Stack traces are useless** - The crash happens far from the actual problem

Our existing monitoring showed:
```bash
# What we could see
✅ API response times: Normal (2-3 seconds)
✅ CPU usage: Healthy (30-40%)
✅ Database connections: Stable
❌ Memory usage: "It goes up sometimes" 🤷‍♂️
```

**The Real Issue:** We had no function-level memory visibility. We knew *something* was eating memory, but not *what* or *when*.

## The Solution: If You Can't Buy It, Build It

After two days of fruitless debugging, I decided to take a different approach. Instead of guessing, I'd build a tool to **see exactly what was happening**.

### The Requirements

I needed something that could:
1. **Track memory usage per function** - Not just overall app memory
2. **Work with existing NestJS code** - No major refactoring
3. **Be production-safe** - Toggle on/off without breaking anything
4. **Provide detailed logs** - Function name, memory consumed, execution time
5. **Handle both sync and async functions** - Our API had both

### Building the Memory Profiler

I created what became the [`@mahabub-arafat/memory-profiler`](https://www.npmjs.com/package/@mahabub-arafat/memory-profiler) package. Here's how it works:

#### The Core Concept: Decorators That Measure

```typescript
import { Injectable } from '@nestjs/common';
import { ProfileAllMethods } from '@mahabub-arafat/memory-profiler';

@Injectable()
@ProfileAllMethods()  // 🎯 This is the magic
export class FlightService {
    async getAvailableFlights() {
        // Your existing code - no changes needed
    }

    async getFlightHistory() {
        // This is where the leak was hiding
    }
}
```

#### What Happens Under the Hood

The decorator wraps each method and:

1. **Captures start memory**: `process.memoryUsage().heapUsed`
2. **Executes the original function**
3. **Captures end memory** and calculates difference
4. **Logs everything** with beautiful, color-coded output

```typescript
// Simplified version of the core logic
function profileMemory(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
        const startMemory = process.memoryUsage().heapUsed / 1024 / 1024;
        const startTime = Date.now();
        
        const result = await originalMethod.apply(this, args);
        
        const endMemory = process.memoryUsage().heapUsed / 1024 / 1024;
        const executionTime = Date.now() - startTime;
        const memoryConsumed = endMemory - startMemory;
        
        logger.info(`Function: ${propertyName}, Memory: ${memoryConsumed.toFixed(2)}MB, Time: ${executionTime}ms`);
        
        return result;
    };
}
```

## The Hunt: Deploying the Detective

### Setting Up in Production

```bash
# Environment setup
ENABLE_MEMORY_PROFILING_DECORATOR=true
```

```typescript
// Applied to our suspicious services
@Injectable()
@ProfileAllMethods()
export class FlightService {
    // All methods now being monitored
}

@Injectable()
@ProfileAllMethods() 
export class BookingService {
    // Every function call tracked
}
```

### The Smoking Gun

Within hours, the logs revealed the culprit:

```bash
INFO [2024-10-23 10:51:53.710 +0600]: Function: getAvailableFlights, Memory: -0.95MB, Time: 2450ms ✅
INFO [2024-10-23 10:52:15.442 +0600]: Function: createBooking, Memory: 2.3MB, Time: 1200ms ✅
WARN [2024-10-23 10:52:45.123 +0600]: Function: getFlightHistory, Memory: 847.32MB, Time: 8900ms ⚠️
```

**There it was.** The `getFlightHistory` function was consuming **847MB** in a single call. In a normal application, that's astronomical.

## The Root Cause: A Tale of Missing Data

### The Investigation

I dove into the `getFlightHistory` function:

```typescript
async getFlightHistory(providerId: string, bookingCode?: string) {
    const filter: any = { providerId };
    
    // The bug was here ⬇️
    if (bookingCode) {
        filter.bookingCode = bookingCode;
    }
    
    // This query was the problem
    return await this.flightHistoryRepository.find(filter);
}
```

### The Eureka Moment

For one specific provider, the third-party API wasn't sending `bookingCode` in their responses. So our filter became:

```typescript
// What we expected
filter = { providerId: "PROVIDER_123", bookingCode: "ABC123" }

// What actually happened
filter = { providerId: "PROVIDER_123" }  // bookingCode was undefined
```

**The Result:** Instead of returning one specific flight record, we were returning **the entire flight history table** for that provider. Thousands of records. Hundreds of megabytes. Every. Single. Time.

### The Cascade Effect

```bash
# What happened in production
User requests flight history → Missing bookingCode → Return entire table → 
Memory spike → Multiply by concurrent users → Heap overflow → App crash
```

## The Fix: Simple but Critical

```typescript
async getFlightHistory(providerId: string, bookingCode?: string) {
    const filter: any = { providerId };
    
    // The fix ✅
    if (!bookingCode) {
        throw new BadRequestException('Booking code is required');
    }
    
    filter.bookingCode = bookingCode;
    return await this.flightHistoryRepository.find(filter);
}
```

**Result:** Memory usage dropped from 847MB to 2.3MB per call. Problem solved.

## The Impact: More Than Just a Bug Fix

### Immediate Results
- **🚀 Zero crashes** after the fix
- **💰 Revenue protection** - No more booking interruptions  
- **😌 Team relief** - The mystery was finally solved
- **📊 Memory visibility** - We could now see what we couldn't before

### Long-term Benefits
- **Published the package** on [NPM](https://www.npmjs.com/package/@mahabub-arafat/memory-profiler) for the community
- **Proactive monitoring** - We now profile new services by default
- **Faster debugging** - Similar issues get caught in hours, not days
- **Team confidence** - We have the tools to solve production mysteries

## The Package: Built for Real-World Use

### Key Features

```typescript
// Profile everything in a class
@ProfileAllMethods()
export class SomeService { }

// Profile individual functions
@ProfileMemoryAsyncFunction()
async specificMethod() { }

@ProfileMemorySyncFunction()
syncMethod() { }
```

### Production-Safe Design

- **Environment toggle**: Only runs when `ENABLE_MEMORY_PROFILING_DECORATOR=true`
- **Zero performance impact** when disabled
- **Beautiful logging** with `pino` and color coding
- **TypeScript support** out of the box

### Real Output in Action

```bash
INFO [2024-10-23 10:51:53.710 +0600] (776639 on st): 
  Async -> Function: getAvailableFlights, 
  startMemory: 45.57MB, endMemory: 44.62MB, 
  memoryConsumed: -0.95MB, executionTime: 2450 ms

WARN [2024-10-23 10:52:21.261 +0600] (776639 on st): 
  Async -> Function: timedoutSearch, 
  startMemory: 42.17MB, endMemory: 36.15MB, 
  memoryConsumed: -6.02MB, executionTime: 30000 ms
```

## Lessons Learned: The Real Takeaways

### 1. Build the Tools You Need
Sometimes the solution isn't in existing tools. When you can't find what you need, build it. The time invested in creating the right tool pays dividends.

### 2. Function-Level Monitoring Matters
Application-level metrics miss the details. Function-level visibility reveals the real culprits hiding in your codebase.

### 3. Memory Leaks Are Sneaky
They don't always look like traditional leaks. Sometimes it's just one function doing too much work, too often.

### 4. Production Debugging Requires Production Tools
Development tools often can't replicate production scenarios. Build tools that work safely in production.

### 5. Share Your Solutions
Publishing the package helped other developers facing similar issues. Open source makes everyone stronger.

## What's Next: The Future of Memory Monitoring

I'm working on v2 of the memory profiler with:
- **Heap dump integration** for deeper analysis
- **Memory trend tracking** over time
- **Automatic alerting** for memory spikes
- **Integration with APM tools** like New Relic and DataDog

## Try It Yourself

Want to add function-level memory monitoring to your NestJS app?

```bash
npm install @mahabub-arafat/memory-profiler
```

Check out the full documentation on [GitHub](https://github.com/mahabubarafat-st/memory-profiler) and [NPM](https://www.npmjs.com/package/@mahabub-arafat/memory-profiler).

---

**The Bottom Line:** Sometimes the best debugging tool is the one you build yourself. When production is on fire and traditional tools aren't helping, don't be afraid to create something new. You might just save the day - and help other developers in the process.

*Have you ever built custom debugging tools to solve production issues? I'd love to hear your stories. Connect with me on [LinkedIn](https://linkedin.com/in/mahabubarafat) - let's share war stories and solutions.*
