var navbar = new Vue({
  el: '#navbar'
})

var ctx = document.getElementById('chart').getContext('2d');
var chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        datasets: [
        {
            label: '% of occurring as leading digit to satisfy Benford\'s law',
            data: [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6],
            backgroundColor: 'rgba(255, 128, 0, 0.6)'
        },
        {
            label: '% of occurring as leading digit in data',
            data: [],
            backgroundColor: 'rgba(0, 128, 255, 0.6)'
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});

var analysis_section = new Vue({
  el: '#analysis-section',
  data() {
    return {
      stats: undefined,                         // statistics with benfords law analysis
      lead_frequenters: undefined,              // lead frequenters provides data for digits
      ben: {'value': 0.0, 'variant': 'danger'}, // current column benford's law compliant
      data: undefined,
    }
  },
  methods: {
    set: function(stats, lead_frequenters) {
        this.stats = stats;
        this.lead_frequenters = lead_frequenters;

        // get columns names
        let columns = Object.keys(lead_frequenters);
        file_columns.populate_columns(columns);
    },
    /*
        Updating chart with new dataset from `lead_frequenters`
    */
    update_chart: function(column) {
        this.ben['pvalue'] = this.stats['benford'][column];                         // get benfords law results
        this.ben['value'] = Number((this.ben['pvalue'] * 100.0).toFixed(4));        // set value as pval * 100
        this.ben['variant'] = this.ben['pvalue'] >= 0.95 ? 'success' : 'danger';    // set proper prompt

        let lead_frequenter = this.lead_frequenters[column];    // pick proper frequenter and set data
        var new_data = [];
        for (const i of Array(9).keys()) {
            const digit = (i + 1).toString(); // starts from 1 to 0
            new_data.push(lead_frequenter[digit])
        }

        chart.data.datasets[1].data = new_data;
        chart.update();
    }
  },
  delimiters: ['[[', ']]']
})

var files_section = new Vue({
  el: '#files-section',
  data() {
    return {
      selected: undefined,  // file selected from list
      files: undefined,     // available files to analyze (as filenames)
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
      show: false,      // when uploading, loading overlay is applied
      file: undefined,  // file which will be uploaded after hitting 'Upload' button
    }
  },
  methods: {
    focus_btn: function() {
        this.$refs['file-upload-btn'].focus(); // after browse file selected, focus on upload button
    },
    upload: function() {
      this.show = true;   // show that file's uploading
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
            this.show = false;  // let upload new file now
            file_analyze.$refs['file-analyze-btn'].focus(); // focus on analyze button
        })
        .catch(error => {
            this.show = false;  // let upload new file now here too
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
      show: false,              // when uploading, loading overlay is applied
      selected_ext: undefined,  // selected file extension
      extensions: undefined,    // available extensions
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
    analyze: function() {
        this.show = true;   // show that analysis' working
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
            let stats = response.data.stats;                        // statistics with benfords law analysis
            let lead_frequenters = response.data.lead_frequenters;  // frequenters for each column in data
            analysis_section.set(stats, lead_frequenters);
            this.show = false;                                      // let do analysis again
            file_columns.$refs['file-columns-select'].focus();      // focus on column select
            file_analyze.$bvToast.toast(`File has been analyzed, now select column`, {
              title: 'Success',
              variant: 'success',
              autoHideDelay: 2000
            });
        })
        .catch(error => {
            this.show = false;                                      // let do analysis again here too
            if (error.response === undefined) {
                file_analyze.$bvToast.toast(`Undefined error happend`, {
                  title: 'Error',
                  variant: 'danger',
                  autoHideDelay: 2000
                });
                return;
            }
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

var file_columns = new Vue({
  el: '#file-columns',
  data() {
    return {
      columns: undefined,   // columns from analyzed file
      selected_col: null,   // selected by user column
      def_column: { value: null, text: 'Select column', disabled: true },
    }
  },
  mounted() {
    this.refresh();
  },
  methods: {
    refresh: function() {   // set single disabled column with text 'Select column'
        this.columns = [this.def_column];
        this.selected_col = null;
    },
    populate_columns: function(columns) {   // after file analysis, columns should be updated
        this.refresh();
        columns.push(this.def_column);
        this.columns = columns;
    },
    update_chart: function() {  // after selecting column chart should be updated
        if (this.selected_col !== undefined) {
            analysis_section.update_chart(this.selected_col);
        }
    }
  },
  delimiters: ['[[', ']]']
})