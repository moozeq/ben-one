var navbar = new Vue({
  el: '#navbar',
  data() {
    return {}
  },
  methods: {
    help() {
        console.log('Not implemented');
    }
  }
})


var analysis_section = new Vue({
  el: '#analysis-section',
  data() {
    return {
      plot: null
    }
  },
  methods: {
  }
})

var files_section = new Vue({
  el: '#files-section',
  data() {
    return {
      user_files: undefined,
      others_files: undefined,
      file: undefined,
    }
  },
  mounted () {
    this.init();
  },
  methods: {
    init: function() {
        axios
          .get('/api/analyses')
          .then(response => {
            this.user_files = response.data.user_files;
            this.others_files = response.data.others_files;
          });
    },
    upload() {
      let formData = new FormData();
      formData.append('file', this.file);

      axios.post('/api/upload',
          formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        ).then(function() {
            files_section.$bvToast.toast(`File has been uploaded`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });
        })
        .catch(function() {
            files_section.$bvToast.toast(`Could not upload file`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        });
    }
  }
})