<script setup></script>

<template>
  <form method="post" action="/apply" autocomplete="on">
    <div class="checkbox-container">
      <label for="url">下载地址:</label>
      <input type="text" placeholder="https://www.bilibili.com/bv" required name="url" />
    </div>
    <div class="checkbox-container" v-for="(section, key) in config" :key="key">
      <label :for="key" :title="key">{{ section.description }}</label>
      <input
        v-if="section.type == 'checkbox'"
        :type="section.type"
        :checked="section.checked"
        :value="section.value"
        :name="key"
      />
      <input
        v-if="section.type == 'text'"
        :type="section.type"
        :placeholder="section.placeholder"
        :value="section.value"
        :required="section.required"
        :name="key"
      />
    </div>
    <button type="submit">Submit</button>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      config: null,
      form: FormData
    }
  },
  mounted() {
    this.fetchConfig()
  },
  methods: {
    async fetchConfig() {
      try {
        const response = await axios.get('/api/config')
        this.config = response.data
        console.log(this.config)
      } catch (error) {
        console.error('Error fetching config:', error)
      }
    }
  }
}
</script>

<style scoped>
.checkbox-container {
  display: flex;
  align-items: center;
}

.checkbox-container label,
.checkbox-container input[type='text'] {
  margin-left: 1em;
  margin-right: 1em;
}
</style>
