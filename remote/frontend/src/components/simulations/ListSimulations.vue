<template>
  <div>
    <h1>Simulations</h1>
    <b-button :to="'/create-simulation'" type="button" variant="primary">Create simulations ...</b-button>
    <table class="table">
      <thead>
        <tr>
          <th scope="col"></th>
          <th scope="col">Name</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="simulation in simulations" v-bind:key="simulation.id">
          <td><b-button :to="'/simulation/' + simulation.id + '/delete'" type="button" class="btn btn-sm btn-danger">X</b-button></td>
          <td><b-link :to="'/simulation/' + simulation.id + '/show'">{{ simulation.name }}</b-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ListSimulations',
  data: function() {
    return {
      simulations: []
    };
  },
  created: function () {
    axios.get("http://localhost:5000/simulations")
    .then(response => {
      this.simulations = response.data;
    })
    .catch(error => {
      alert(error);
    });
  }
}
</script>
