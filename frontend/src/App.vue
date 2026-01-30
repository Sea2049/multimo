<template>
  <router-view />
  <ErrorAlert ref="errorAlertRef" @retry="handleRetry" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ErrorAlert from './components/ErrorAlert.vue'
import { setErrorAlertsRef } from './composables/useErrorHandler'

const errorAlertRef = ref(null)

const handleRetry = async (item) => {
  if (item.retryFn && typeof item.retryFn === 'function') {
    try {
      await item.retryFn()
    } catch (error) {
      console.error('Retry failed:', error)
    }
  }
}

onMounted(() => {
  if (errorAlertRef.value) {
    setErrorAlertsRef(errorAlertRef.value)
  } else {
    console.warn('[App] ErrorAlert component failed to mount')
  }
})
</script>

<style>
/* Modern CSS Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body,
h1, h2, h3, h4, h5, h6,
p,
figure,
blockquote,
dl, dd {
  margin: 0;
}

ul, ol {
  margin: 0;
  padding: 0;
  list-style: none;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {      
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* Focus visible styles for accessibility */
:focus-visible {
  outline: 2px solid #000;
  outline-offset: 2px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {
  outline: 2px solid #000;
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
