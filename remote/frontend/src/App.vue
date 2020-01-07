<template>
  <div id="app">
    <Navigation />
    <div class="container-fluid">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
//import HelloWorld from './components/HelloWorld.vue'
import Navigation from './components/Navigation.vue'

export default {
  name: 'app',
  components: {
    Navigation
  }
}
</script>
