<template>
  <router-view />
  <ErrorAlert ref="errorAlertRef" @retry="handleRetry" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ErrorAlert from './components/ErrorAlert.vue'
import { setErrorAlertsRef } from './composables/useErrorHandler'

const errorAlertRef = ref(null)

const handleRetry = (item) => {
  console.log('Retry action triggered:', item)
}

onMounted(() => {
  if (errorAlertRef.value) {
    setErrorAlertsRef(errorAlertRef.value)
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
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

button {
  font-family: inherit;
}
</style>
