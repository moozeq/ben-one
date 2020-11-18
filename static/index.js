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
      stats: undefined,
      benfords_law: undefined,
      counters: undefined,
      frequenters: undefined,
      lead_frequenters: undefined,
      ben_data: undefined,
      data: undefined,
    }
  },
  methods: {
    set: function(stats, benfords_law, counters, frequenters, lead_frequenters) {
        this.stats = stats;
        this.benfords_law = benfords_law;
        this.counters = counters;
        this.frequenters = frequenters;
        this.lead_frequenters = lead_frequenters;

        // get columns names
        let columns = Object.keys(lead_frequenters);
        file_columns.populate_columns(columns);
    },
    update_chart: function(column) {
        this.ben_data = 'Benfor\'s law pvalue = ' + this.benfords_law[column];
        let lead_frequenter = this.lead_frequenters[column];

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
    upload: function() {
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
    analyze: function() {
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
            let stats = response.data.stats;
            let benfords_law = response.data.benfords_law;
            let counters = response.data.counters;
            let frequenters = response.data.frequenters;
            let lead_frequenters = response.data.lead_frequenters;
            analysis_section.set(stats, benfords_law, counters, frequenters, lead_frequenters);
            file_analyze.$bvToast.toast(`File has been analyzed, now select column`, {
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

var file_columns = new Vue({
  el: '#file-columns',
  data() {
    return {
      columns: undefined,
      selected_col: null,
      def_column: { value: null, text: 'Select column' },
    }
  },
  mounted() {
    this.refresh();
  },
  methods: {
    refresh: function() {
        this.columns = [this.def_column];
        this.selected_col = null;
    },
    populate_columns: function(columns) {
        this.refresh();
        columns.push(this.def_column);
        this.columns = columns;
    },
    update_chart: function() {
        if (this.selected_col !== undefined) {
            analysis_section.update_chart(this.selected_col);
        }
    }
  },
  delimiters: ['[[', ']]']
})