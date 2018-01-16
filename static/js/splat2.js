$(function() {
    $("#show-about").click(function() {
        $('body').css('overflow','hidden')
        $(".about-popup").fadeIn("slow");
        return false;
    });
    $("#close-about").click(function() {
        $('body').css('overflow','auto')
        $(".about-popup").fadeOut("slow");
        return false;
    });
});
$(function() {
    $("#show-credits").click(function() {
        $('body').css('overflow','hidden')
        $(".credit-popup").fadeIn("slow");
        return false;
    });
    $("#close-credits").click(function() {
        $('body').css('overflow','auto')
        $(".credit-popup").fadeOut("slow");
        return false;
    });
});