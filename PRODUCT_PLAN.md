# MileProfit — Product Launch Plan

> Turn MileProfit from working MVP into a shippable, monetized product for TVDE drivers.

---

## Vision

A dead-simple PWA that helps TVDE/ride-sharing drivers answer one question:
**"Am I actually making money?"**

Track earnings, expenses, and mileage. See real profitability. Know when driving isn't worth it.

---

## Current State

- Working FastAPI + Vue 3 PWA
- Auth, earnings, expenses, mileage tracking, dashboard charts
- Single-user deployable on Hetzner via Docker Compose
- No payments, no tests, several security gaps

---

## Phases

---

### Phase 0 — Fix Critical Gaps (Before Showing Anyone)

> ~1 week. Non-negotiable before any real user touches this.

| Task | Why |
|------|-----|
| Move `SECRET_KEY` out of `config.py` into real env secret | Hardcoded — security hole |
| Lock CORS to production domain | Currently defaults to localhost |
| Rate limit `/api/auth/login` | Brute-force open |
| Switch SQLite → PostgreSQL | SQLite corrupts under concurrent writes |
| Set up automated DB backups | Data loss = trust loss |
| Add JWT refresh token rotation | 24h token expiry with no refresh = bad UX |

**Exit criteria:** App runs on Postgres, secrets in env, login rate-limited, DB backed up daily.

---

### Phase 1 — Auth & Onboarding (Week 2–3)

> Users need to self-register. Right now accounts are created via CLI.

| Task | Detail |
|------|--------|
| Self-registration flow | Email + password signup in frontend |
| Email verification | Verify email before granting access |
| Password reset | "Forgot password" → email link |
| Welcome / onboarding screen | Guide new user to log first trip |

**Tools needed:** Transactional email (Resend or Postmark — simple API, cheap).

**Exit criteria:** User can sign up, verify email, reset password without admin CLI.

---

### Phase 2 — Legal & Compliance (Week 3–4)

> Required in EU/Portugal. You collect personal financial data — GDPR applies.

| Task | Detail |
|------|--------|
| Privacy Policy | What data collected, how stored, retention period |
| Terms of Service | Usage rules, liability, account termination |
| Cookie/analytics consent banner | Only if adding any analytics |
| GDPR: data export endpoint | User can download all their data |
| GDPR: account deletion | User can delete account + all data |

**Exit criteria:** Legal pages live, data export + delete working, GDPR-compliant.

---

### Phase 3 — Observability (Week 4–5)

> You can't fix what you can't see.

| Task | Detail |
|------|--------|
| Sentry (backend) | Catch and alert on Python exceptions |
| Sentry (frontend) | Catch Vue errors, network failures |
| Structured request logging | FastAPI middleware → logs with request ID, latency |
| Uptime monitor | Betterstack or UptimeRobot — alert on downtime |
| Global FastAPI error handler | Return consistent JSON errors, not 500 stack traces |
| Vue error boundary | Top-level `errorCaptured` — catch and show friendly UI |

**Exit criteria:** Any unhandled error surfaces in Sentry within 1 minute.

---

### Phase 4 — Monetization (Week 5–7)

> Pick a model. Suggested: freemium with Stripe.

#### Pricing Model (suggestion)

| Tier | Price | Limits |
|------|-------|--------|
| Free | €0 | Last 30 days of data, no export |
| Pro | €4.99/month or €39/year | Unlimited history, CSV export, detailed reports |

#### Tasks

| Task | Detail |
|------|--------|
| Stripe integration (backend) | Checkout session, webhook handler, subscription status |
| Stripe customer portal | Self-serve cancel/upgrade |
| Plan enforcement middleware | Block Pro features for free users |
| Upgrade prompt in UI | Show contextual prompts when hitting free limits |
| Billing page in settings | Show current plan, next billing date, manage button |

**Exit criteria:** User can upgrade to Pro, downgrade, and cancel entirely without touching the server.

---

### Phase 5 — PWA Completeness (Week 7–8)

> App installs but offline mode is broken. PWA promise not delivered.

| Task | Detail |
|------|--------|
| Offline data access | Cache last-fetched dashboard + history in IndexedDB |
| Offline entry queuing | Log trip while offline → sync when back online |
| Push notifications | Weekly earnings summary (opt-in) |
| iOS home screen testing | Test install + behaviour on Safari/iOS |
| Android Chrome testing | Test install + behaviour on Chrome/Android |

**Exit criteria:** User can log a trip with no internet connection. It syncs on reconnect.

---

### Phase 6 — CI/CD & Tests (Ongoing, start Week 2)

> Ship with confidence. Zero tests right now.

| Task | Detail |
|------|--------|
| GitHub Actions pipeline | Lint + test on every PR |
| Backend unit tests | Auth, earnings CRUD, mileage calculations (pytest) |
| Frontend component tests | Key views with Vitest |
| E2E smoke tests | Login → log trip → see dashboard (Playwright) |
| Automated deploy on merge to main | `deploy.sh` triggered via GitHub Actions + SSH |

**Exit criteria:** Green CI required to merge. Deploy is one `git push`.

---

## Feature Backlog (Post-Launch)

These add value but aren't required to ship.

- **CSV/PDF export** — earnings report for tax purposes (huge for TVDE drivers)
- **Per-platform breakdown** — Uber vs Bolt vs others, separate tracking
- **Vehicle cost tracking** — depreciation, insurance, maintenance
- **Profitability by time-of-day / day-of-week** — heatmap view
- **Goal setting** — "I want to earn €X this month"
- **Multi-vehicle** — some drivers run 2 cars
- **Referral program** — drivers talk to drivers
- **iOS/Android native wrapper** — Capacitor if PWA limitations become painful

---

## Infrastructure Upgrades (When Scaling)

Current single-Hetzner-server setup is fine up to ~500 active users. Beyond that:

| Upgrade | Trigger |
|---------|---------|
| Managed PostgreSQL (Hetzner or Supabase) | >100 users or any data reliability concern |
| Separate backend/frontend servers | CPU bottleneck |
| CDN for frontend assets (Cloudflare) | Users outside PT complain about speed |
| Redis for rate limiting + sessions | Rate limiter needs shared state across instances |

---

## Launch Checklist

- [ ] Phase 0 complete (security fixes, Postgres)
- [ ] Self-registration working
- [ ] Legal pages live (Privacy Policy, ToS)
- [ ] Sentry integrated
- [ ] Stripe Pro tier working
- [ ] Uptime monitor active
- [ ] Custom domain + HTTPS (Let's Encrypt)
- [ ] App tested on iOS Safari + Android Chrome
- [ ] At least 5 beta users have signed up and used it
- [ ] Password reset flow tested end-to-end

---

## Timeline Summary

| Phase | Focus | Duration |
|-------|-------|----------|
| 0 | Security & infrastructure fixes | Week 1 |
| 1 | Auth & onboarding | Week 2–3 |
| 2 | Legal & GDPR | Week 3–4 |
| 3 | Observability | Week 4–5 |
| 4 | Monetization (Stripe) | Week 5–7 |
| 5 | PWA completeness | Week 7–8 |
| 6 | CI/CD + tests | Ongoing from Week 2 |

**Target: first paying user by Week 8.**
