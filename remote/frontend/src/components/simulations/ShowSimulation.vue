<template>
  <div>
    <h1>Simulation: {{ simulation.name }}</h1>
    <b-button :to="'/simulation/' + simulation.id + '/delete'" type="button" class="btn btn-sm btn-danger">Delete environment</b-button>
    <br /><br />
    <b-card title="General">
      Name: {{ simulation.name }}
    </b-card><br />
    <!--b-card title="Assets">
      <b>Upload</b>
    </b-card-->
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ShowSimulation',
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
  }
}
</script>
