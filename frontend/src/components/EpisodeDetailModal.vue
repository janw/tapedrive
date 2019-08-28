<template>
  <div v-if="item">
    <b-container fluid>
      <h1 class="mb-3">{{item.title}}</h1>
      <b-row class="mb-4">
        <b-col v-html="item.description"></b-col>
      </b-row>

      <b-row class="mb-4">
        <b-col>
          <div
            class="d-flex justify-content-around flex-wrap px-0 py-2 border-top border-bottom text-center"
          >
            <div>
              <p class="text-muted mb-0">Published</p>
              <p class="mb-0">{{item.published | moment("from")}}</p>
            </div>
            <div v-if="item.downloaded" class>
              <p class="text-muted mb-0">Downloaded</p>
              <p class="mb-0">{{item.downloaded | moment("from")}}</p>
            </div>
          </div>
        </b-col>
      </b-row>

      <div v-if="item.chapters" class="row mb-2">
        <div class="col">
          <p class="text-center">
            <b-button v-b-toggle.collapse-chapters variant="outline-secondary">Show Chapters</b-button>
          </p>
          <b-collapse id="collapse-chapters" class="mt-2">
            <table class="table table-hover">
              <tr>
                <th>Timestamp</th>
                <th>Title</th>
              </tr>
              <tr v-for="chapter in item.chapters" :key="chapter.id">
                <td class="text-muted">
                  <small>{{chapter.starttime}}</small>
                </td>
                <td>{{chapter.title}}</td>
              </tr>
            </table>
          </b-collapse>
        </div>
      </div>
      <b-row class="mb-3">
        <b-col v-html="item.shownotes"></b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  props: ["item"]
};
</script>