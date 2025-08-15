/**
 * EU-Compliant Cookie Consent Banner
 * GDPR/CCPA compliant cookie consent management
 */

class CookieConsent {
    constructor() {
        this.consentKey = 'cookie_consent_v1';
        this.consentData = this.getStoredConsent();
        this.init();
    }

    init() {
        // Only show banner if consent hasn't been given
        if (!this.consentData) {
            this.showConsentBanner();
        } else {
            // Load consented services
            this.loadConsentedServices();
        }
    }

    getStoredConsent() {
        try {
            const stored = localStorage.getItem(this.consentKey);
            return stored ? JSON.parse(stored) : null;
        } catch (e) {
            return null;
        }
    }

    storeConsent(consent) {
        try {
            const consentData = {
                ...consent,
                timestamp: new Date().toISOString(),
                version: 1
            };
            localStorage.setItem(this.consentKey, JSON.stringify(consentData));
            this.consentData = consentData;
        } catch (e) {
            console.warn('Could not store cookie consent');
        }
    }

    showConsentBanner() {
        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.innerHTML = `
            <div class="cookie-consent-content">
                <div class="cookie-consent-text">
                    <h3>🍪 Cookie Consent</h3>
                    <p>We use cookies to enhance your browsing experience, analyze site traffic, and display personalized advertisements. By clicking "Accept All", you consent to our use of cookies.</p>
                    <p><a href="privacy-policy.html" target="_blank">Learn more in our Privacy Policy</a></p>
                </div>
                <div class="cookie-consent-buttons">
                    <button id="cookie-accept-essential" class="cookie-btn cookie-btn-essential">Essential Only</button>
                    <button id="cookie-customize" class="cookie-btn cookie-btn-customize">Customize</button>
                    <button id="cookie-accept-all" class="cookie-btn cookie-btn-accept">Accept All</button>
                </div>
            </div>
            <div id="cookie-preferences" class="cookie-preferences" style="display: none;">
                <h4>Cookie Preferences</h4>
                <div class="cookie-category">
                    <label class="cookie-toggle">
                        <input type="checkbox" id="essential-cookies" checked disabled>
                        <span class="toggle-slider"></span>
                        <div class="cookie-info">
                            <strong>Essential Cookies</strong>
                            <p>Required for basic site functionality. Cannot be disabled.</p>
                        </div>
                    </label>
                </div>
                <div class="cookie-category">
                    <label class="cookie-toggle">
                        <input type="checkbox" id="analytics-cookies">
                        <span class="toggle-slider"></span>
                        <div class="cookie-info">
                            <strong>Analytics Cookies</strong>
                            <p>Help us understand how visitors interact with our website.</p>
                        </div>
                    </label>
                </div>
                <div class="cookie-category">
                    <label class="cookie-toggle">
                        <input type="checkbox" id="advertising-cookies">
                        <span class="toggle-slider"></span>
                        <div class="cookie-info">
                            <strong>Advertising Cookies</strong>
                            <p>Used to display relevant advertisements based on your interests.</p>
                        </div>
                    </label>
                </div>
                <div class="cookie-preferences-buttons">
                    <button id="cookie-save-preferences" class="cookie-btn cookie-btn-accept">Save Preferences</button>
                    <button id="cookie-back" class="cookie-btn cookie-btn-essential">Back</button>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            <style>
            #cookie-consent-banner {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #fff;
                border-top: 3px solid #0073e6;
                box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
                padding: 20px;
                z-index: 10000;
                font-family: Arial, sans-serif;
                max-height: 90vh;
                overflow-y: auto;
            }

            .cookie-consent-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                gap: 20px;
                flex-wrap: wrap;
            }

            .cookie-consent-text {
                flex: 1;
                min-width: 300px;
            }

            .cookie-consent-text h3 {
                margin: 0 0 10px 0;
                color: #333;
                font-size: 1.2em;
            }

            .cookie-consent-text p {
                margin: 5px 0;
                color: #666;
                font-size: 0.9em;
                line-height: 1.4;
            }

            .cookie-consent-text a {
                color: #0073e6;
                text-decoration: none;
            }

            .cookie-consent-text a:hover {
                text-decoration: underline;
            }

            .cookie-consent-buttons {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .cookie-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9em;
                font-weight: bold;
                transition: all 0.3s ease;
            }

            .cookie-btn-accept {
                background: #0073e6;
                color: white;
            }

            .cookie-btn-accept:hover {
                background: #005bb5;
            }

            .cookie-btn-essential {
                background: #6c757d;
                color: white;
            }

            .cookie-btn-essential:hover {
                background: #545b62;
            }

            .cookie-btn-customize {
                background: #f8f9fa;
                color: #333;
                border: 2px solid #dee2e6;
            }

            .cookie-btn-customize:hover {
                background: #e9ecef;
            }

            .cookie-preferences {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
            }

            .cookie-preferences h4 {
                margin: 0 0 15px 0;
                color: #333;
            }

            .cookie-category {
                margin: 15px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
            }

            .cookie-toggle {
                display: flex;
                align-items: center;
                gap: 15px;
                cursor: pointer;
            }

            .cookie-toggle input[type="checkbox"] {
                display: none;
            }

            .toggle-slider {
                width: 50px;
                height: 24px;
                background: #ccc;
                border-radius: 12px;
                position: relative;
                transition: background 0.3s;
                flex-shrink: 0;
            }

            .toggle-slider::before {
                content: '';
                position: absolute;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: white;
                top: 2px;
                left: 2px;
                transition: transform 0.3s;
            }

            .cookie-toggle input:checked + .toggle-slider {
                background: #0073e6;
            }

            .cookie-toggle input:checked + .toggle-slider::before {
                transform: translateX(26px);
            }

            .cookie-toggle input:disabled + .toggle-slider {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .cookie-info strong {
                display: block;
                color: #333;
                margin-bottom: 5px;
            }

            .cookie-info p {
                margin: 0;
                color: #666;
                font-size: 0.85em;
            }

            .cookie-preferences-buttons {
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }

            @media (max-width: 768px) {
                .cookie-consent-content {
                    flex-direction: column;
                    text-align: center;
                }

                .cookie-consent-buttons {
                    justify-content: center;
                    width: 100%;
                }

                .cookie-btn {
                    flex: 1;
                    min-width: 120px;
                }
            }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.appendChild(banner);

        this.attachEventListeners();
    }

    attachEventListeners() {
        // Accept all cookies
        document.getElementById('cookie-accept-all')?.addEventListener('click', () => {
            this.acceptAllCookies();
        });

        // Essential cookies only
        document.getElementById('cookie-accept-essential')?.addEventListener('click', () => {
            this.acceptEssentialOnly();
        });

        // Show customization options
        document.getElementById('cookie-customize')?.addEventListener('click', () => {
            this.showCustomization();
        });

        // Save custom preferences
        document.getElementById('cookie-save-preferences')?.addEventListener('click', () => {
            this.saveCustomPreferences();
        });

        // Back to main banner
        document.getElementById('cookie-back')?.addEventListener('click', () => {
            this.hideCustomization();
        });
    }

    acceptAllCookies() {
        const consent = {
            essential: true,
            analytics: true,
            advertising: true
        };
        this.storeConsent(consent);
        this.loadConsentedServices();
        this.hideBanner();
    }

    acceptEssentialOnly() {
        const consent = {
            essential: true,
            analytics: false,
            advertising: false
        };
        this.storeConsent(consent);
        this.loadConsentedServices();
        this.hideBanner();
    }

    showCustomization() {
        document.querySelector('.cookie-consent-content').style.display = 'none';
        document.getElementById('cookie-preferences').style.display = 'block';
    }

    hideCustomization() {
        document.querySelector('.cookie-consent-content').style.display = 'flex';
        document.getElementById('cookie-preferences').style.display = 'none';
    }

    saveCustomPreferences() {
        const consent = {
            essential: true, // Always true
            analytics: document.getElementById('analytics-cookies').checked,
            advertising: document.getElementById('advertising-cookies').checked
        };
        this.storeConsent(consent);
        this.loadConsentedServices();
        this.hideBanner();
    }

    hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.animation = 'slideDown 0.5s ease-out forwards';
            setTimeout(() => banner.remove(), 500);
        }
    }

    loadConsentedServices() {
        if (!this.consentData) return;

        // Load Google AdSense if advertising cookies are consented
        if (this.consentData.advertising) {
            this.loadGoogleAdSense();
        }

        // Load Google Analytics if analytics cookies are consented
        if (this.consentData.analytics) {
            this.loadGoogleAnalytics();
        }

        // Set Google Consent Mode
        this.setGoogleConsentMode();
    }

    loadGoogleAdSense() {
        // This will be populated with your actual AdSense code
        if (window.adsbygoogle_loaded) return;
        
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX';
        script.crossOrigin = 'anonymous';
        document.head.appendChild(script);
        
        window.adsbygoogle_loaded = true;
        console.log('Google AdSense loaded with consent');
    }

    loadGoogleAnalytics() {
        // Placeholder for Google Analytics
        // You can add GA4 code here if needed
        console.log('Google Analytics would be loaded here');
    }

    setGoogleConsentMode() {
        // Google Consent Mode v2
        if (typeof gtag !== 'undefined') {
            gtag('consent', 'update', {
                'analytics_storage': this.consentData.analytics ? 'granted' : 'denied',
                'ad_storage': this.consentData.advertising ? 'granted' : 'denied',
                'ad_user_data': this.consentData.advertising ? 'granted' : 'denied',
                'ad_personalization': this.consentData.advertising ? 'granted' : 'denied'
            });
        }
    }

    // Public method to show preferences again
    showPreferences() {
        this.showConsentBanner();
        this.showCustomization();
    }

    // Public method to reset consent
    resetConsent() {
        localStorage.removeItem(this.consentKey);
        this.consentData = null;
        location.reload();
    }
}

// Add slide animation styles
const animationStyles = `
    <style>
    @keyframes slideDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(100%); opacity: 0; }
    }
    </style>
`;
document.head.insertAdjacentHTML('beforeend', animationStyles);

// Initialize cookie consent when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cookieConsent = new CookieConsent();
});

// Make it available globally for preference management
window.CookieConsent = CookieConsent;
