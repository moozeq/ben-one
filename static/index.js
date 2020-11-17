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
      stats: undefined,
      counters: undefined,
    }
  },
  methods: {
    set: function(stats, counters) {
        this.stats = stats;
        this.counters = counters;
    }
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
        ).then(response => {
            files_section.$bvToast.toast(`File has been uploaded`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });
        })
        .catch(error => {
            files_section.$bvToast.toast(`Could not upload file: ${error.response.data.error}`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        });
    },
    analyze(mode) {
      axios.post('/api/analyze', {'filename': this.file.name, 'mode': mode}
        ).then(response => {
            analysis_section.set(response.data.stats, response.data.counters);
            files_section.$bvToast.toast(`File has been analyzed`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });

        })
        .catch(error => {
            files_section.$bvToast.toast(`Could not analyze file: ${error.response.data.error}`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        });
    }
  }
})