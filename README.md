# GigShield — AI-Powered Parametric Income Insurance for Food Delivery Workers

**Guidewire DEVTrails 2026 | Phase 1 — Ideate & Know Your Delivery Worker**

---

## The Problem We're Solving

Every day, millions of Zomato and Swiggy delivery riders wake up knowing that their income depends entirely on one thing — being able to ride through the city. When a red-alert flood hits Mumbai, when Delhi's AQI spikes past 400, when an unexpected curfew shuts down a zone — they can't work. No orders, no earnings, no recourse.

The problem isn't that these disruptions happen. It's that there is no financial safety net when they do. Standard health insurance doesn't cover lost wages. Vehicle insurance covers the bike, not the person's livelihood. The rider simply absorbs the loss.

According to the problem statement, a single disruption event can wipe 20–30% of a gig worker's monthly income. Most of these workers earn between ₹15,000–25,000 a month. They have no savings buffer. They live week to week, sending money home, paying rent, managing a two-wheeler loan — all on the assumption that they can work every day the weather allows.

GigShield is a parametric income insurance platform that pays them automatically when that assumption breaks down.

---

## Our Persona: Food Delivery Partners on Zomato and Swiggy

We chose food delivery over grocery or e-commerce delivery for a specific reason: the income disruption from weather events is the most direct and the most measurable. When it rains heavily enough that deliveries stop, we know exactly which zone was affected, for how long, and what the platform's operational status was. That clean data linkage between external event and income loss is what makes parametric insurance viable here.

**Who we are building for:**

A typical Zomato rider in Bengaluru is 26 years old, migrated from a smaller city, works 8–10 hours a day, six days a week. He earns around ₹700 on a good day. He pays ₹4,500 a month in room rent, sends ₹3,000 home, manages a two-wheeler EMI of ₹2,200, and has roughly ₹2,000 left at the end of the month. When three days of flooding hit his zone in July, he doesn't have a buffer. He calls his landlord and asks for a few more days.

We are not building insurance for that rider's health. We are not covering his bike. We are covering exactly one thing: **the income he lost because the world outside made it impossible for him to work.**

**Scenario — Arjun, Mumbai, a Wednesday in July:**

Arjun is on his sixth delivery of the morning when the IMD red alert fires for Andheri East. The rain turns heavy by 10:40am. Swiggy pauses orders in the zone at 11:00am. Arjun pulls over under a flyover and sits. He has a ₹45 Rakshak policy active this week.

At 10:52am, GigShield's trigger engine detects that rainfall in Arjun's zone has crossed 20mm/hr and has sustained for 2 hours. It checks: Is Arjun covered this week? Yes. Was he showing active shift signals in the last 90 minutes? Yes — his last order was delivered at 10:38am. Is his location inside the affected IMD zone polygon? Yes.

At 11:02am, a payout of ₹480 initiates. At 11:09am, it hits his UPI. He gets a WhatsApp message: *"Arjun bhai, aaj Andheri East mein baarish ka red alert aaya. Aapka ₹480 UPI pe bhej diya gaya hai. Rakshak plan ke tahat."*

He didn't file a claim. He didn't call anyone. He didn't even know he was going to be paid until the money arrived.

---

## How the Application Works

The platform has four core flows that connect the worker's experience to the underlying parametric engine.

**Registration and Onboarding**

The worker downloads the GigShield app, signs up with their phone number, and completes a lightweight KYC using Aadhaar (mocked in our prototype). They then connect their delivery platform profile through our simulated Swiggy/Zomato API integration. This step pulls two key data points: the zones they have delivered in over the past 30 days, and their average daily earnings. The system uses these to calculate their personalised weekly premium before they even choose a tier.

We designed onboarding to take under 4 minutes and to require zero insurance literacy. The worker is never asked to read policy documents or understand terms. They are asked two things: which tier do you want, and confirm your primary delivery zones. The AI handles the rest.

**Weekly Policy Selection**

On Monday, the worker chooses or renews their weekly coverage. The app shows them their dynamic premium for the week — adjusted for current zone risk forecasts, the season, and their own claims history. They pay once. The policy auto-renews the following Monday unless they pause it. Workers who want more coverage heading into monsoon season can upgrade tiers week to week.

**Trigger Monitoring and Claim Initiation**

Our trigger pipeline runs continuously, pulling data from five external sources every few minutes. When a disruption crosses a defined threshold in a worker's active zone, and the worker passes the on-shift verification check (described below), a claim initiates automatically. The worker does not need to do anything. This is the core promise of parametric insurance: the trigger is objective, the payout is automatic, there is no subjectivity in the claim decision.

**Payout and Communication**

Once a claim initiates, the fraud detection layer runs in the background. For claims that pass, money reaches the worker's UPI in under 10 minutes. They receive a WhatsApp notification in Hindi or English that explains exactly what happened — which event, which zone, how much, when. The message is generated by our LLM layer and is designed to feel like it came from a person, not a system.

For claims that need additional verification, the worker receives a one-tap confirmation prompt. They never have to call anyone or wait for a callback.

---

## Weekly Premium Model

Our financial model is structured weekly because gig workers think and operate weekly. A ₹45/week premium is a decision a rider can make on Monday morning. A ₹2,340/year premium is not.

We offer three tiers:

**Saathi — ₹20/week — Maximum payout ₹400/week**
For part-time workers or those who operate in historically lower-risk zones. Covers the basics without overcommitting on premium.

**Rakshak — ₹45/week — Maximum payout ₹900/week**
Our primary tier, designed for full-time workers in moderate-risk zones. Priced to be roughly 5–6% of a typical weekly earning — affordable but meaningful coverage.

**Suraksha — ₹80/week — Maximum payout ₹1,600/week**
For full-time workers in high-risk zones or during peak monsoon season. Provides near-full income replacement for a disrupted week.

We named the tiers in Hindi — Saathi means companion, Rakshak means protector, Suraksha means safety — because the product is built for people who speak Hindi, not insurance jargon.

**Dynamic Pricing Within Tiers**

The tier defines the maximum payout. The actual weekly premium a worker pays is calculated by an XGBoost regression model that personalises their rate based on four variables:

*Zone risk score:* We divide each city into 2km grid cells and compute a historical disruption frequency score based on 12 months of IMD rainfall and AQICN data. A worker who primarily delivers in Dharavi — which floods regularly — pays a higher zone multiplier than one who works in Powai. This is the kind of hyper-local risk pricing the problem statement specifically asks for, and it's what makes the premium feel fair rather than arbitrary.

*Shift exposure:* A rider who works 9 hours a day is on the road roughly twice as long as one who works 4 hours. More hours means more exposure to disruption events. The model adjusts accordingly.

*Season multiplier:* We apply a seasonal risk factor that increases premiums during the monsoon months (June–September for Mumbai, July–August for Delhi, June–October for Chennai) and during documented heatwave periods. This refreshes monthly using IMD seasonal forecasts.

*Loyalty factor:* Workers with 6 or more months of clean claims history receive a 10% discount. This rewards honest usage and reduces adverse selection over time.

In practice, Arjun in Andheri East (high flood risk, 9 hrs/day) on the Rakshak tier pays ₹63/week. Rahul in Bandra (lower flood risk, 5 hrs/day) on the same Rakshak tier pays ₹38/week. Same tier, different risk, different price — and both workers can see exactly why.

We chose XGBoost for this model specifically because it produces interpretable outputs. In a regulated insurance context, we need to be able to explain to an IRDAI auditor why any given premium is set at any given amount. Gradient boosted trees give us that explainability; deep learning models do not.

---

## Parametric Triggers

We defined five triggers based on what actually stops food delivery workers from being able to work in Indian cities. Each threshold is anchored to a real operational or safety benchmark — not an arbitrary number.

**Trigger 1 — Heavy Rainfall**
Data source: India Meteorological Department radar API and OpenWeatherMap
Threshold: Rainfall exceeding 20mm/hr sustained for 2 or more consecutive hours
Payout: 100% of the worker's covered daily wage
Reasoning: Platform companies themselves use approximately this rainfall intensity as the threshold for surge pricing and operational restrictions on delivery. It is the industry-validated point at which deliveries effectively halt. We are not setting an arbitrary number — we are mirroring the operational reality.

**Trigger 2 — Severe Air Quality**
Data source: AQICN real-time API (free tier, covers all Tier-1 Indian cities with sub-hourly updates)
Threshold: AQI above 400, the Severe+ category on India's National Air Quality Index
Payout: 75% of covered daily wage (partial, acknowledging that some workers push through at this level)
Reasoning: At AQI 400+, SAFAR (the government's air quality forecasting body) officially recommends avoiding all outdoor physical activity. We verified with documented rider union activity in Delhi that strikes and work stoppages cluster at this threshold.

**Trigger 3 — Flood Alert**
Data source: IMD Flood Warning Services (official government alerts, zone-level granularity)
Threshold: Red alert issued for the worker's registered primary delivery zone
Payout: 100% of covered daily wage
Reasoning: A red-alert flood warning means the zone is physically inaccessible. There is zero delivery activity during these periods. The trigger is binary and objective.

**Trigger 4 — Extreme Heat**
Data source: OpenWeatherMap current conditions API
Threshold: Temperature sustained above 45°C for 3 or more consecutive hours
Payout: 50% of covered daily wage
Reasoning: At 45°C, sustained outdoor activity constitutes a documented occupational health hazard under Indian labour guidelines. We pay 50% rather than 100% because heat is a more gradual disruption — some workers reduce hours rather than stop entirely, and our partial payout acknowledges that reality while still providing meaningful support.

**Trigger 5 — Curfew or Zone Shutdown**
Data source: Official state government notification RSS feeds, cross-verified using a lightweight news NLP classifier we will build in Phase 2
Threshold: Verified zone-level restriction lasting 4 or more hours, confirmed by at least two independent government sources
Payout: 100% of covered daily wage
Reasoning: Unplanned curfews and sudden hartals (local strikes causing zone closures) happen frequently in Indian cities — especially around political events, accidents, or civil incidents. Workers have no warning and no ability to reroute. The 4-hour minimum prevents brief road closures from triggering payouts.

One constraint we enforce strictly across all triggers: **we are insuring income lost during these events, not any expense caused by them.** No medical bills. No vehicle repair. No property damage. The policy covers exactly one thing — hours the worker couldn't work because of an external disruption.

---

## AI and ML Integration

We are integrating AI in four specific places in the platform. Each one solves a real problem in our workflow — not one of them is AI for its own sake.

**1. Dynamic Premium Calculation — XGBoost Regression**

This is the model that makes our per-worker pricing possible. We train an XGBoost regression model on zone-level historical disruption data combined with simulated worker profiles across 5 cities. The model outputs a weekly premium multiplier for each worker based on their risk profile.

Feature inputs include zone_flood_days_past_12m, zone_aqi_exceedance_days_past_12m, avg_daily_shift_hours, current_month_season_risk_score, worker_claims_history_clean_flag, and zone_centroid_lat_lng. The model produces a multiplier that the system applies to the worker's base tier price each Monday.

We retrain this model monthly with updated IMD and AQICN zone data to keep the pricing current with seasonal risk changes.

**2. Claim Eligibility Scoring — Random Forest Classifier**

Before any fraud check runs, a Random Forest classifier evaluates whether a triggered claim is legitimately eligible. This catches edge cases: a worker whose shift ended 3 hours before the flood hit, a worker in Zone A whose policy covers Zone B, a duplicate trigger for the same event.

Input features include trigger_magnitude_vs_threshold_ratio, worker_zone_overlap_pct, hours_since_last_platform_activity, shift_active_at_event_time_flag, and event_polygon_overlap_score. Output is an eligibility confidence score from 0–100. Claims below 60 are held before fraud scoring even begins.

**3. Fraud Detection and Ring Analysis — Gradient Boosted Classifier**

This is covered in detail in the Anti-Spoofing section. The ML layer produces a fraud confidence score using 8 independent behavioral signals. The score routes the claim to one of three handling tiers: automatic approval, soft confirmation request, or manual human review.

We also run a parallel ring detection analysis that looks for coordinated fraud patterns across groups of claims — something that individual scoring alone cannot catch.

**4. LLM Communication Layer — GPT-4o-mini via LangChain**

This is the feature that makes GigShield feel different from any other insurance product a delivery worker has ever encountered — which for most of them is nothing at all, or a confusing platform health insurance form they never understood.

When a payout triggers, the LLM generates a personalised WhatsApp message in Hindi or English. Not a template — a contextual message that names the specific event, the specific zone, the specific amount, and when it will arrive. The tone is that of a helpful colleague, not an insurance company.

When an insurer admin opens their Monday dashboard, instead of raw loss ratio numbers they read a plain-English narrative: *"This week, Zone 4 in Whitefield had 3 AQI exceedance events. 47 claims were auto-approved at an average of ₹380 each. Loss ratio for the zone is 68%, up from 51% last week. We recommend reviewing the monsoon-season premium multiplier for this zone before next renewal cycle."*

When a fraud reviewer opens a flagged claim, they don't see a number — they read: *"This claim was flagged because the worker's GPS coordinates place them in Indiranagar, but their phone is connecting through a cell tower in Marathahalli, approximately 14km away. Their last confirmed delivery was 7 hours before the trigger event. Fraud confidence score: 38/100."*

The LLM never makes a decision. The ML models decide. The LLM translates those decisions into language that workers trust and reviewers can act on. That is the two-stage architecture — ML for precision, LLM for communication — that we believe represents the right way to build AI into a financial product that affects real people's lives.

---

## Platform Choice: Mobile-First with a Web Admin Dashboard

We are building a React Native mobile app for delivery workers (iOS and Android from a single codebase) and a React web dashboard for insurer administrators.

The reason for mobile-first is not a technical preference — it is a user reality. Delivery workers do not use laptops. They check their earnings between deliveries on a ₹7,000–10,000 Android phone. They pay rent on UPI. Every interaction we design has to work on a mid-range device with a variable 4G connection that may drop during the exact weather events that trigger their claims. That constraint shaped every design decision: single-action flows, large tap targets, offline status caching for claims, and a WhatsApp integration for notifications because WhatsApp is already the communication layer of their daily life.

The admin dashboard is web-based because insurer operations staff work at desktops and need dense data views — loss ratio by zone, fraud review queues, weekly trend charts, predictive next-week risk forecasts — that do not translate to mobile screens.

---

## Adversarial Defense & Anti-Spoofing Strategy

*This section was added in direct response to the Market Crash scenario issued on March 20, 2026, which described a 500-person coordinated syndicate using GPS-spoofing applications to fake claim locations.*

We want to be direct about something: we did not treat this as a compliance checkbox. We treated it as the most important design challenge in the platform, because a parametric insurance system that can be gamed by location spoofing is not an insurance system — it is a money printer for anyone with the right app. The entire model breaks down if the trigger verification can be faked.

Here is our approach.

**The On-Shift Gate: The First and Most Important Check**

Before any fraud scoring runs, every triggered claim must pass an on-shift verification gate. This checks one question: did this worker show confirmed delivery platform activity within 90 minutes of the trigger event?

Confirmed activity means an order accepted, a delivery completed, or a location ping logged by the Swiggy/Zomato platform API in the worker's registered zone. If the answer is no — if the worker was effectively idle on the platform before the disruption hit — no claim initiates. Not even tentatively.

This single gate eliminates the largest class of GPS spoofing fraud: someone at home who opens a spoofing app after seeing a flood alert on the news. They were never working. They have no claim. The gate does not require any ML — it is a simple logical check against platform activity data.

This approach was a core design insight from PwC's GigGuards platform (DEVHack 2025 winner), which won in part because its coverage activated only during active working hours. We adapted that principle as our primary fraud prevention layer.

**The 8-Signal Behavioral Fingerprint**

For claims that pass the on-shift gate, our fraud classifier evaluates eight independent signals. A genuine worker in a flood zone will show a consistent pattern across most of these. A GPS spoofer at home will show inconsistencies that, even if they appear plausible individually, become statistically unlikely in combination.

*Signal 1 — Cell tower triangulation:* Every phone connects to a physical cell tower. We cross-reference the claimed GPS coordinates against the coverage area of the device's serving tower. A worker claiming to be in Andheri East while connecting through a Borivali tower (18km away) generates an immediate flag. GPS spoofing apps change the software-reported GPS coordinates. They do not change which tower the phone physically connects to.

*Signal 2 — Accelerometer and gyroscope pattern:* A rider who was genuinely working before a flood hit carries 45 minutes of motion data consistent with riding — acceleration bursts, braking patterns, turn events, the characteristic micro-vibration of a two-wheeler on Indian roads. A phone sitting on a table at home shows a flat accelerometer signature. We analyse the motion history in the 45-minute window before the claim trigger.

*Signal 3 — Platform activity recency and zone match:* Via our simulated platform API, we retrieve the worker's last confirmed delivery event: the zone it was in, how long ago it was, and whether that zone is consistent with the claimed disruption location. A genuine worker caught in a flood had recent deliveries in the affected area. A spoofer at home has stale location history from a different part of the city.

*Signal 4 — Historical delivery zone pattern:* We maintain 90 days of delivery zone history per worker, built from platform activity data collected at registration and during active weeks. If a worker has never delivered in the zone they are claiming to be stranded in, that is a strong fraud indicator. Most GPS spoofers select high-risk zones without checking whether the worker has any delivery history there.

*Signal 5 — Device integrity markers:* Common GPS spoofing applications available on Android leave identifiable traces in device metadata and permission logs. We check for the presence of known spoofing app signatures as part of claim processing.

*Signal 6 — Weather microzone polygon validation:* We validate that the worker's GPS coordinates fall inside the precise IMD-issued polygon for the specific disruption event — not just anywhere in the city. A worker faking their location to "Mumbai during the flood" but placing their GPS outside the actual 2km rain polygon gets caught at this step. City-level faking is common; polygon-level faking requires knowing the exact boundary of each IMD event zone, which is not public information.

*Signal 7 — Battery and screen state consistency:* An active delivery rider has battery drain and screen usage patterns consistent with navigation apps, camera use (delivery photo confirmation), and order management. A phone idle at home shows different power and screen usage patterns. This signal has lower weight in our composite score but contributes to the overall picture.

*Signal 8 — Network environment type:* Genuine riders in rain are outdoors, connecting via mobile data on a variable signal. Workers at home are typically on WiFi with stable signal strength. We include network type and signal stability as a soft signal — not determinative alone, but meaningful in combination.

**Detecting Coordinated Fraud Rings**

The scenario described a syndicate of 500 workers coordinating via Telegram. Individual fraud scoring is not built to detect this — each individual claim might score borderline acceptable while the collective pattern is clearly fraudulent.

We layer ring detection logic on top of individual claim scoring:

*Cluster trigger:* If 12 or more workers whose registered home locations (identified from their consistent GPS-at-rest pattern during registration) fall within a 500-meter radius all submit claims within an 8-minute window, the entire batch is flagged for ring review — regardless of individual confidence scores.

*Tower concentration check:* If a group of claims shows GPS coordinates spread across a zone but all connecting through 2 or fewer cell towers, that is geometrically inconsistent. Real workers spread across a 2km area connect through different towers. Coordinated spoofing from a single apartment building all routes through the same local tower.

*Submission pattern analysis:* Genuine disruptions cause claims to arrive as a gradual ramp — workers realise the disruption is serious, stop working, and submit over a 20–40 minute window. A coordinated attack via Telegram produces a spike: many claims arriving within 2–3 minutes of each other. We analyse the arrival time distribution of claims per zone per event and flag spike patterns for ring review.

Ring-flagged claim batches go to a dedicated fraud queue with a 4-hour review SLA. Workers in a ring-flagged batch receive the standard Amber-tier response (described below) — they are not told they are under review, and the honest workers among them still receive 50% of their payout immediately.

**The Three-Tier Response: Protecting Honest Workers**

This is where we think most fraud systems fail: they flag too aggressively and end up penalising genuine workers who happen to have a weak GPS signal, a dead phone, or a genuine network drop during the same weather event that caused their income loss. That destroys trust in the product faster than any fraud ever would.

Our three tiers:

*Green — confidence above 80%:* Full payout auto-approved. Money arrives in under 10 minutes. Worker receives a Hindi WhatsApp explaining the payout. No action required from them. This is the experience we want for every genuine claim.

*Amber — confidence 55–80%:* We split the response immediately. 50% of the payout initiates automatically — so a genuine worker is never left with nothing while we verify. We send a single WhatsApp message: *"Hum verify kar rahe hain ki aap disruption ke time zone mein the. Ek tap karo confirm karne ke liye."* One tap confirms. If the worker confirms within 3 hours, the remaining 50% releases instantly. This tier exists specifically for genuine workers with a spotty connection in bad weather — they get half immediately and only need to confirm once when they get signal back.

*Red — confidence below 55%:* Full payout held. Worker receives a transparent notification: we need to verify their location during the disruption, here is an appeal link, here is what to submit, we will respond within 24 hours. A human reviewer receives the case with the LLM-generated fraud summary. No claim is permanently denied on a first flag without a human making that decision.

Our target is fewer than 2% false positives on Green-tier decisions — meaning that 98 out of 100 auto-approved claims are legitimate. We would rather occasionally pay a fraudulent claim than create a system that honest workers cannot trust.

---

## Tech Stack

| Component | Technology | Why this choice |
|-----------|-----------|----------------|
| Worker app | React Native (iOS + Android) | Single codebase for both platforms; performs well on mid-range Android; strong India developer community |
| Admin dashboard | React with Recharts | Best ecosystem for the data-dense insurer views we need; recharts for zone heatmaps and loss ratio charts |
| ML service | FastAPI (Python) | Native Python for scikit-learn and XGBoost; async; production-appropriate for model serving |
| Trigger pipeline | Node.js with WebSocket | Real-time event processing with low latency; WebSocket for live dashboard updates |
| ML models | XGBoost, Random Forest, scikit-learn | Best-in-class for tabular insurance data; interpretable outputs for regulatory compliance |
| LLM layer | GPT-4o-mini via LangChain | Cost-effective for message generation at scale; LangChain handles prompt versioning and fallbacks |
| Primary database | PostgreSQL | ACID compliance is non-negotiable for financial records and policy state |
| Cache | Redis | Sub-millisecond reads for the trigger event cache and active policy lookups |
| Cloud | AWS Lambda + EC2 + S3 | Lambda for trigger functions (event-driven, scales to zero); EC2 for ML model server; S3 for zone polygon data |
| Weather data | OpenWeatherMap API + IMD RSS | OpenWeatherMap for real-time conditions; IMD for official India flood and heat alerts |
| Air quality | AQICN API (free tier) | Best free-tier AQI coverage for Indian cities; sub-hourly updates |
| Payments | Razorpay test mode | Standard India payment gateway; robust UPI sandbox available |
| Auth | Firebase Authentication | Handles OTP-based phone authentication cleanly; well-tested on low-end Android |
| DevOps | GitHub Actions + Docker | CI/CD from day one; Docker for environment parity between local and production |

---

## Development Plan

**Phase 1 — Completed with this document**

Persona research and scenario definition, system architecture, weekly premium model and tier design, parametric trigger selection with threshold justification, full AI/ML plan including model choices and feature specifications, anti-spoofing strategy, tech stack finalised, GitHub repository set up.

**Phase 2 — March 21 to April 4: Protect Your Worker**

Worker registration and onboarding flow in React Native, guided by the LLM onboarding chatbot. Policy creation with live dynamic premium calculation running the XGBoost model. Parametric trigger pipeline end-to-end with at least 3 working triggers — we will implement rainfall, AQI, and flood alert first, using live API data where available and mocks where not. Claims management with on-shift gate, cell tower mismatch check, and accelerometer pattern check as the first fraud layer. Razorpay sandbox payout integration. LLM-generated claim notifications in Hindi and English. 2-minute demo video showing the full worker flow from policy purchase to payout.

**Phase 3 — April 5 to April 17: Perfect Your Worker**

Full 8-signal fraud classifier with ring detection logic. Instant payout pipeline with end-to-end latency under 10 minutes from trigger to UPI credit. Worker dashboard showing active coverage status, this week's earnings protected, and claim history. Insurer admin dashboard with zone-level loss ratios, fraud queue with LLM summaries, weekly AI-generated narrative report, and predictive next-week risk forecast by zone. 5-minute demo video demonstrating a simulated rainstorm trigger flowing through to an automatic payout and a Hindi WhatsApp notification. Final pitch deck PDF covering the delivery persona, AI and fraud architecture, and weekly pricing business model.



## Team-204

1. Priyanshu Kumar Singh (Team Leader), 
2. Saurabh Kumar Singh, 
3. Devesh Kumar Yadav, 
4. Ravi Shankar Tiwari,
5. Shubham Yadav  
