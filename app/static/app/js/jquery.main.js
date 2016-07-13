jQuery(document).ready(function($) {

    var heightdiv = $('.horizontal-one').height();

    $(".vertical-one img").css({
        'height': heightdiv
    });

    $(".vertical-two img").css({
        'height': heightdiv + heightdiv - 1 + 'px'
    });


    $('#nav').slicknav();

    //Menu
    $("ul.navigation").superfish({
        delay: 3000,
        animation: {
            opacity: "show",
            height: "show"
        },
        speed: "normal"
    });

    //Select
    $('select:not([multiple])').idealselect();

    //Date
    $('form.idealforms.searchtours').idealforms({
        rules: {
            'event': 'date'
        }
    });

    //Add ride
    $('form.idealforms.add-ride').idealforms({
        rules: {
            'event': 'date'
        }
    });

    //Parallax
    if ("ontouchstart" in window) {
        document.documentElement.className = document.documentElement.className + " touch";
    }
    if (!$("html").hasClass("touch")) {
        /* background fix */
        $(".parallax").css("background-attachment", "fixed");
    }

    /* fix vertical when not overflow
     call fullscreenFix() if .fullscreen content changes */
    function fullscreenFix() {
        var h = $('.main-baner').height();
        // set .fullscreen height
        $(".second-parallax-content").each(function(i) {
            if ($(this).innerHeight() <= h) {
                $(this).closest(".fullscreen").addClass("not-overflow");
            }
        });
    }
    $(window).resize(fullscreenFix);
    fullscreenFix();
    /* resize background images */
    function backgroundResize() {
        var windowH = $(window).height();
        $(".background").each(function(i) {
            var path = $(this);
            // variables
            var contW = path.width();
            var contH = path.height();
            var imgW = path.attr("data-img-width");
            var imgH = path.attr("data-img-height");
            var ratio = imgW / imgH;
            // overflowing difference
            var diff = parseFloat(path.attr("data-diff"));
            diff = diff ? diff : 0;
            // remaining height to have fullscreen image only on parallax
            var remainingH = 0;
            if (path.hasClass("parallax") && !$("html").hasClass("touch")) {
                var maxH = contH > windowH ? contH : windowH;
                remainingH = windowH - contH;
            }
            // set img values depending on cont
            imgH = contH + remainingH + diff;
            imgW = imgH * ratio;
            // fix when too large
            if (contW > imgW) {
                imgW = contW;
                imgH = imgW / ratio;
            }
            //
            path.data("resized-imgW", imgW);
            path.data("resized-imgH", imgH);
            path.css("background-size", imgW + "px " + imgH + "px");
        });
    }
    $(window).resize(backgroundResize);
    $(window).focus(backgroundResize);
    backgroundResize();
    /* set parallax background-position */
    function parallaxPosition(e) {
        var heightWindow = $(window).height();
        var topWindow = $(window).scrollTop();
        var bottomWindow = topWindow + heightWindow;
        var currentWindow = (topWindow + bottomWindow) / 2;
        $(".parallax").each(function(i) {
            var path = $(this);
            var height = path.height();
            var top = path.offset().top;
            var bottom = top + height;
            // only when in range
            if (bottomWindow > top && topWindow < bottom) {
                var imgW = path.data("resized-imgW");
                var imgH = path.data("resized-imgH");
                // min when image touch top of window
                var min = 0;
                // max when image touch bottom of window
                var max = -imgH + heightWindow;
                // overflow changes parallax
                var overflowH = height < heightWindow ? imgH - height : imgH - heightWindow; // fix height on overflow
                top = top - overflowH;
                bottom = bottom + overflowH;
                // value with linear interpolation
                var value = min + (max - min) * (currentWindow - top) / (bottom - top);
                // set background-position
                var orizontalPosition = path.attr("data-oriz-pos");
                orizontalPosition = orizontalPosition ? orizontalPosition : "50%";
                $(this).css("background-position", orizontalPosition + " " + value + "px");
            }
        });
    }
    if (!$("html").hasClass("touch")) {
        $(window).resize(parallaxPosition);
        $(window).scroll(parallaxPosition);
        parallaxPosition();
    }

    //Counter
    $('.counter').counterUp({
        delay: 10,
        time: 1000
    });

    //Tooltip
    $('.tooltip-link').tooltip();


    //Login
    $('form.idealforms.login').idealforms({
        silentLoad: false,
        rules: {
            'username': 'required username',
            'password': 'required password'
        },
        onSubmit: function(e) {
            e.preventDefault();
        }
    });

    //Registration
    $('form.idealforms.reg').idealforms({
        silentLoad: false,
        rules: {
            'username': 'required username',
            'email': 'required email',
            'password': 'required pass',
            'confirmpass': 'required equalto:password'
        },
        onSubmit: function(e) {
            e.preventDefault();
        }
    });

    //Registration
    $('form.idealforms.add-post').idealforms({
        silentLoad: false,
        rules: {
            'destination': 'select:default'
        },
        onSubmit: function(e) {
            e.preventDefault();
        }
    });


});
