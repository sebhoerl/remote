<template>
  <div>
    <h1>Really Delete simualtion? : {{ simulation.name }}</h1>
    <b-button v-on:click="perform_delete" variant="danger">Delete!</b-button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeleteSimulation',
  data: function() {
    return {
      simulation: {}
    };
  },
  created: function () {
    axios.get("http://localhost:5000/simulation/" + this.$route.params.id)
    .then(response => {
      this.simulation = response.data;
    })
    .catch(error => {
      alert(error);
    });
  },
  methods: {
    perform_delete: function() {
      axios.delete("http://localhost:5000/simulation/" + this.simulation.id)
      .then(response => {
        response;
        this.$router.push("/simulations");
      })
      .catch(error => {
        alert(error);
      });
    }
  }
}
</script>
