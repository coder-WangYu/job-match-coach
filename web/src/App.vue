<script setup>
import AppHeader from './components/app-header.vue';
import { useRoute } from 'vue-router';

const route = useRoute()
</script>

<template>
  <AppHeader v-if="route.meta.showHeader" />
  <router-view />
</template>