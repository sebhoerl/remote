<template>
  <div>
    <h1>Environment: {{ environment.name }}</h1>
    <b-button :to="'/environment/' + environment.id + '/delete'" type="button" class="btn btn-sm btn-danger">Delete environment</b-button>
    <br /><br />
    <b-card title="General">
      Type: {{ environment.type }}
    </b-card><br />
    <!--b-card title="Assets">
      <b>Upload</b>
    </b-card-->
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ShowEnvironment',
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
  }
}
</script>
