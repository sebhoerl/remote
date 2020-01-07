<template>
  <div>
    <h1>Really Delete environment? : {{ environment.name }}</h1>
    <b-button v-on:click="perform_delete" variant="danger">Delete!</b-button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeleteEnvironment',
  data: function() {
    return {
      environment: {}
    };
  },
  created: function () {
    axios.get("http://localhost:5000/environment/" + this.$route.params.id)
    .then(response => {
      this.environment = response.data;
    })
    .catch(error => {
      alert(error);
    });
  },
  methods: {
    perform_delete: function() {
      axios.delete("http://localhost:5000/environment/" + this.environment.id)
      .then(response => {
        response;
        this.$router.push("/environments");
      })
      .catch(error => {
        alert(error);
      });
    }
  }
}
</script>
