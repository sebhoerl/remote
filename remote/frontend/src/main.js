import '@babel/polyfill'
import 'mutationobserver-shim'
import Vue from 'vue'
import './plugins/bootstrap-vue'
import App from './App.vue'

import VueRouter from 'vue-router'
Vue.use(VueRouter)

Vue.config.productionTip = false

import ListEnvironments from './components/environments/ListEnvironments.vue'
import DeleteEnvironment from './components/environments/DeleteEnvironment.vue'
import ShowEnvironment from './components/environments/ShowEnvironment.vue'
import CreateEnvironment from './components/environments/CreateEnvironment.vue'

import ListSimulations from './components/simulations/ListSimulations.vue'
import DeleteSimulation from './components/simulations/DeleteSimulation.vue'
import ShowSimulation from './components/simulations/ShowSimulation.vue'
import CreateSimulation from './components/simulations/CreateSimulation.vue'

import Runs from './components/Runs.vue'

const routes = [
  { path: "/environments", component: ListEnvironments },
  { path: "/create-environment", component: CreateEnvironment },
  { path: "/environment/:id/show", component: ShowEnvironment },
  { path: "/environment/:id/delete", component: DeleteEnvironment },
  { path: "/simulations", component: ListSimulations },
  { path: "/create-simulation", component: CreateSimulation },
  { path: "/simulation/:id/show", component: ShowSimulation },
  { path: "/simulation/:id/delete", component: DeleteSimulation },
  { path: "/runs", component: Runs },
]

const router = new VueRouter({ routes })

new Vue({
  render: h => h(App), router
}).$mount('#app')
