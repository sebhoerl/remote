<template>
  <div>
    <h1>Create environment</h1>
    <b-form @submit="perform_create_environment">
      <b-card header="General">
        <b-form-group label="Unique ID" label-cols="3">
          <b-form-input v-model="environment.id"></b-form-input>
        </b-form-group>
        <b-form-group label="Name" label-cols="3">
          <b-form-input v-model="environment.name"></b-form-input>
        </b-form-group>
        <b-form-group label="Type" label-cols="3">
          <b-form-select v-model="environment.type" :options="types"></b-form-select>
        </b-form-group>
      </b-card>
      <br />
      <b-card header="Environment">
        <b-form-group label="Type" label-cols="3">
          <b v-if="environment.type == 'local'">Local</b>
          <b v-if="environment.type == 'ssh'">SSH</b>
          <b v-if="environment.type == 'lsf'">LSF</b>
        </b-form-group>
        <b-form-group label="Server address" label-cols="3" v-if="environment.type != 'local'">
          <b-form-input v-model="environment.server"></b-form-input>
          Currently, we assume public key access. TODO: Add user name and password.
        </b-form-group>
        <b-form-group label="Working directory path" label-cols="3">
          <b-form-input v-model="environment.path"></b-form-input>
        </b-form-group>
      </b-card><br />
      <b-card header="MATSim">
        <b-form-group label="JAVA path" label-cols="3">
          <b-form-input v-model="environment.java_path"></b-form-input>
        </b-form-group>
        <b-form-group label="Data / Assets path" label-cols="3">
          <b-form-input v-model="environment.data_path"></b-form-input>
        </b-form-group>
      </b-card><br />
      <b-button type="submit" variant="primary" :disabled="environment.type == null">Create!</b-button>
    </b-form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateEnvironment',
  data: function() {
    return {
      types: [
        { value: "local", text: "Local" },
        { value: "ssh", text: "SSH" },
        { value: "lsf", text: "LSF" }
      ],
      environment: {
        type: "local",
        name: "My New Environment",
        path: "/path/to/working_directory",
        id: "my_new_environment",
        server: "127.0.0.1",
        java_path: "/usr/bin/java",
        data_path: "/path/to/my/data"
      },
      environment_type: "abc"
    };
  },
  methods: {
    perform_create_environment: function() {
      axios.put("http://localhost:5000/environment/" + this.environment.id, this.environment, { headers: { "Content-Type": "application/json" } })
      .then(response => {
        response;
        this.$router.push("/environments");
      })
      .catch(error => {
        alert(error.response.data["error"]);
      });
    }
  }
}
</script>
