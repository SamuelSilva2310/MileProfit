import { createApp } from 'vue'
import { createPinia } from 'pinia'
import * as Sentry from '@sentry/vue'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'production',
    integrations: [Sentry.browserTracingIntegration({ router })],
    tracesSampleRate: 0.2,
    sendDefaultPii: false,
  })
}

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue error]', info, err)
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.captureException(err, { extra: { info } })
  }
}

app.mount('#app')
