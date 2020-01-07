<template>
  <div>
    <h1>Create simulation</h1>
    <b-form @submit="perform_create_simulation">
      <b-card header="General">
        <b-form-group label="Unique ID" label-cols="3">
          <b-form-input v-model="simulation.id"></b-form-input>
        </b-form-group>
        <b-form-group label="Name" label-cols="3">
          <b-form-input v-model="simulation.name"></b-form-input>
        </b-form-group>
        <b-form-group label="Environments" label-cols="3">
          <b-form-select v-model="simulation.environments" :options="environments" multiple :select-size="4"></b-form-select>
        </b-form-group>
      </b-card><br />
      <b-card header="Simulation">
        <b-form-group label="Config path" label-cols="3">
          <b-form-input v-model="simulation.config_path"></b-form-input>
          You may use %data_path% as a placeholder for the environment's data path property.
        </b-form-group>
        <b-form-group label="Command line parameters" label-cols="3">
          <b-form-input v-model="simulation.parameters"></b-form-input>
        </b-form-group>
      </b-card><br />
      <b-button type="submit" variant="primary">Create!</b-button>
    </b-form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateSimulation',
  data: function() {
    return {
      simulation: {
        config_path: "{data_path}/switzerland_10pct/config.xml",
        parameters: "-Xmx10G"
      },
      environments: []
    };
  },
  created: function () {
    axios.get("http://localhost:5000/environments")
    .then(response => {
      this.environments = [];

      for (var k in response.data) {
        var item = response.data[k];
        this.environments.push({ value: item["id"], text: item["name"] + "(" + item["id"] + ")" });
      }

      this.environments = response.data;
    })
    .catch(error => {
      alert(error);
    });
  },
  methods: {
    perform_create_simulation: function() {
      axios.put("http://localhost:5000/simulation/" + this.simulation.id, this.simulation, { headers: { "Content-Type": "application/json" } })
      .then(response => {
        response;
        this.$router.push("/simulations");
      })
      .catch(error => {
        alert(error.response.data["error"]);
      });
    }
  }
}
</script>
