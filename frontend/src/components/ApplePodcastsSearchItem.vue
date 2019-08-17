<template>
  <a href="#" class="discovery-cover"
     data-toggle="modal" data-target="#apsearch-details" data-id="#"
    @click="$emit('details', result)">
    <img class="img-fluid" :src="result.image" alt="Podcast Cover Art">
  </a>
</template>

<script>
export default {
  props: {
    result: {
      type: Object,
      required: true
    }
  }
}
</script>
