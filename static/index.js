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


var files_section = new Vue({
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
      files: null
    }
  },
  mounted () {
    this.init();
  },
  methods: {
    init: function() {
        axios
          .get('/api/files')
          .then(response => {
            console.log(response.data.files);
            this.files = response.data.files;
          });
    }
  },
  delimiters: ['[[', ']]']
})