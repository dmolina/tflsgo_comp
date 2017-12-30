
var app = new Vue({
    el: '#login',
    data: {
        token:  '',
        message: '',
        benchmark: {},
        bench_user: {},
        error: '',
        error_load: '',
        total_algs: [],
        algs: [],
        sel_algs: []
    },
    methods: {
        login: function(e) {
            var self = this;
            $.ajax(make_ajax_info('login', e)
                  ).done(function(data) {
                      self.token = '';
                      self.error = data['error'];
                      console.log(self.error);

                      if (!self.error) {
                          self.total_algs = data['algs'];
                          console.log(self.total_algs);
                          self.token = data['token'];
                          self.sel_algs = [];
                      }
            }).fail(function(data) {
                self.error = data['error'];
            });
        },
        store: function(e) {
            var self = this;
            self.message = '';

            $.ajax(make_ajax_info('store', e)
                  ).done(function(data) {
                      self.error_load = data['error'];

                      if (!self.error_load) {
                          var new_algs = data['new_algs'];
                          self.total_algs = self.algs.concat(new_algs);
                          var new_algs_str = data['new_algs_str'];
                          self.message = 'Algorithms \'' +new_algs_str +'\' written without error';
                      }
                  }).fail(function(data) {
                      self.error_load = process_fail(data);
                  });
        },
        check_delete: function() {
            var self = this;
            var algs_str = self.sel_algs.toString();
            var result = confirm('Algorithms \'' +algs_str +'\' will be deleted. Are you sure?');

            if (result) {
                data = {'algs_str': algs_str, 'token': self.token, 'benchmark_id': self.bench_user.id};
                $.post('/delete', data).done(
                    function(data) {
                        self.error = data['error'];
                        console.log(self.error);
                        console.log(self.sel_algs);
                        console.log(self.algs);
                        console.log('hola');

                        if (!data['error']) {
                            console.log(self.sel_algs);
                            for (alg in self.sel_algs) {
                                pos = self.algs.indexOf(self.sel_algs[alg]);
                                console.log('pos es \'' +pos.toString() +'\'');
                                self.algs.splice(pos, 1);
                            }

                            self.sel_algs = [];
                        }
                        algs = data['algs'];
                    }).fail(function(data) {
                        self.error = process_fail(data);
                    });
            }
        },
        getmyalgs: function(bench) {
            var self = this;
            var bench_id = bench['id'];

            if (bench_id) {
                var data = {'benchmark_id': bench_id,
                        'token': self.token};
                $.post('/algs', data)
                    .done(function(data) {
                        self.algs = data['algs'];

                    }).fail(function(data) {
                        self.error_load = process_fail(data);
                    });
            }
            else {
                this.algs = [];
            }
        }
    }
});
