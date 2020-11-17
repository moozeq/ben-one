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
  },
  delimiters: ['[[', ']]']
})

var files_section = new Vue({
  el: '#files-section',
  data() {
    return {
      selected: undefined,
      files: undefined,
    }
  },
  mounted() {
    this.refresh();
  },
  methods: {
    refresh: function(selected_file) {
        axios
          .get('/api/files')
          .then(response => {
            this.files = response.data.files;
            // select file if refresh was from file-upload element
            if (selected_file)
                this.select_file(selected_file);
          });
    },
    select_file: function(filename) {
        for (file_idx in this.files) {
            if (filename == this.files[file_idx]) {
                this.selected = file_idx;
                return;
            }
        }
    },
    get_selected: function() {
        return this.files[this.selected];
    },
  },
  delimiters: ['[[', ']]']
})

var file_upload = new Vue({
  el: '#file-upload',
  data() {
    return {
      file: undefined,
    }
  },
  methods: {
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
            file_upload.$bvToast.toast(`File has been uploaded`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });
            files_section.refresh(this.file.name); // refresh and select file
        })
        .catch(error => {
            file_upload.$bvToast.toast(`Could not upload file: ${error.response.data.error}`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        });
    },
  },
  delimiters: ['[[', ']]']
})

var file_analyze = new Vue({
  el: '#file-analyze',
  data() {
    return {
      selected_ext: undefined,
      extensions: undefined,
    }
  },
  mounted() {
    this.refresh();
  },
  methods: {
    refresh: function() {
        axios
          .get('/api/extensions')
          .then(response => {
            this.extensions = response.data.extensions;
            this.selected_ext = this.extensions[0];
          });
    },
    analyze() {
        let filename = files_section.get_selected();
        if (filename == undefined) {
            file_analyze.$bvToast.toast(`Select file first`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        return;
      }
      axios.post('/api/analyze', {'filename': filename, 'ext': this.selected_ext}
        ).then(response => {
            analysis_section.set(response.data.stats, response.data.counters);
            file_analyze.$bvToast.toast(`File has been analyzed`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });

        })
        .catch(error => {
            file_analyze.$bvToast.toast(`Could not analyze file: ${error.response.data.error}`, {
              title: 'Error',
              variant: 'danger',
              autoHideDelay: 2000
            });
        });
    }
  },
  delimiters: ['[[', ']]']
})