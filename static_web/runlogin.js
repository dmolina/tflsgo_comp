var base_url = '';

var app = new Vue({
    el: '#login',
    data: {
        message: '',
        token:  '',
        error: ''
    },
    methods: {
        login: function(e) {
            var self = this;
            e.preventDefault();
            console.log(e.target);
            var formData = new FormData(e.target);

            $.ajax({
                url: base_url +'/login',
                type: 'POST',
                data: formData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false
            }).done(function(data) {
                self.error = '';
                console.log("done");
                self.error = data['error'];

                if (self.error) {
                    self.token = data['token'];
                }
            }).fail(function(data) {
                self.error = '';
                console.log("fail");
                self.error = data['error'];
            });
        }
    }
});
