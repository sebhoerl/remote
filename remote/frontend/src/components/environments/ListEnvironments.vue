<template>
  <div>
    <h1>Environments</h1>
    <b-button :to="'/create-environment'" type="button" variant="primary">Create environment ...</b-button>
    <table class="table">
      <thead>
        <tr>
          <th scope="col"></th>
          <th scope="col">Name</th>
          <th scope="col">Type</th>
          <th scope="col">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="environment in environments" v-bind:key="environment.id">
          <td><b-button :to="'/environment/' + environment.id + '/delete'" type="button" class="btn btn-sm btn-danger">X</b-button></td>
          <td><b-link :to="'/environment/' + environment.id + '/show'">{{ environment.name }}</b-link></td>
          <td>{{ environment.type }}</td>
          <td>TODO</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ListEnvironments',
  data: function() {
    return {
      environments: []
    };
  },
  created: function () {
    axios.get("http://localhost:5000/environments")
    .then(response => {
      this.environments = response.data;
    })
    .catch(error => {
      alert(error);
    });
  }
}
</script>
