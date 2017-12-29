
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
            var result = confirm(self.sel_algs.toString() +' will be deleted. Are you sure?');

            if (result) {
                data = {'algs': self.sel_algs, 'token': self.token};
                $.post('/delete', data).done(
                    function(data) {
                        console.log('delete');
                    });
            }
        },
        getmyalgs: function(bench) {
            var self = this;
            console.log("getmyalgs");
            var bench_id = bench['id'];
            console.log(bench_id);

            if (bench_id) {
                var data = {'benchmark_id': bench_id,
                        'token': self.token};
                $.post('/algs', data)
                    .done(function(data) {
                        console.log("pedido");
                        self.algs = data['algs'];

                    }).fail(function(data) {
                        self.error_load = process_fail(data);
                    });
            }
            else {
                this.algs = [];
                console.log(this.algs);
            }
        }
    }
});
