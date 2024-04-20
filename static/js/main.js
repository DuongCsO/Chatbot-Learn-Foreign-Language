$.getScript("/static/js/common.js");

$(document).ready(() => {

    let message_counter = 1;
function addMessage(sender, message) {
    let html='';
    if (sender === 'user') {
        html = `<div class="post post-user">${message + timeStamp()}</span></div>`;
        $("#message-board").append(html);
    } else {
        playAudio(message,message_counter);
        let translate_icons = `<i class="fa-solid fa-language translate-icons"></i>`;
		let audioButton = `<i class="fa-solid fa-file-audio speak-icons"></i>`;
        html = `
            <div class="post post-bot">
				${message}${timeStamp()}
				${translate_icons}
				${audioButton}
				<span class="translate"></span>
			</div>`;
		$("#message-board").append(html);
		$('.post-bot').on('click', '.translate-icons', function(event) {
			event.stopImmediatePropagation();
			let parent = $(this).closest('.post-bot');
			let translate_span = parent.find('.translate');
			if (translate_span.text() === '') {
			    $.post('/translate_text', {'text': message, 'sender': sender}, function(response) {
			        let translated_text = response['message'].replace(/\n/g, "<br>");
			        translate_span.text(translated_text);
                });
			} else {
				translate_span.empty();
			}
		});
		$('.post-bot').on('click', '.speak-icons', function(event){
			event.stopImmediatePropagation();
            playAudio(message, message_counter);
		});
    }
    $.post('/store_message', {'sender': sender, 'message': message}, function (response) {});
    html.id = "message_" + message_counter;
    message_counter += 1;
}

function playAudio(message, message_index){
            // POST request to /text_to_speech
            $.ajax({
                url: '/text_to_speech',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    message: message,
                    message_index: message_index
                }),
                success: function(response) {
                    let audio = new Audio('static/tmp/bot_speech_'+message_index+'.mp3');
                    audio.play();
                },
                error: function(xhr, status, error) {
                    console.error('Lỗi khi gửi yêu cầu: ', error);
                }
            });
}
//Init Chat
function getResponse(is_initial_message) {
  $.post('/get_response', {'is_initial_message': is_initial_message}, function(response) {
      var bot_message = response['message'];
      var message_index = response['message_index'];
      var error_message = response['error'];
      if (error_message !== null) {
          showNotification(error_message);
      }
      addMessage('assistant', bot_message);
  });
}

function initChat() {
	$('#audio-init').hide();
	$('#main-chat').show();
	getResponse(1);
}


	/******************/
	/*** START CHAT ***/
	/******************/


$(document).ready(function(){
    for (const input_code_and_lang of input_languages_codes_and_names) {  // [iso-6391, language_name]
        $('#user-lang-dropdown').append(new Option(input_code_and_lang[1], input_code_and_lang[0]));
    }
    for (const input_code_and_lang of input_languages_codes_and_names) {  // [language_locale, language_name]
        $('#tutor-lang-dropdown').append(new Option(input_code_and_lang[1], input_code_and_lang[0]));
    }
    $('#form-start').on('submit', function(e) {
        e.preventDefault();  // prevent the form from doing a page refresh
		$("#landing").slideUp(300);
		setTimeout(() => {
			$("#start-chat").html("Continue chat")
		}, 300);
        $.ajax({
            url : $(this).attr('action') || window.location.pathname, // form action url
            type: $(this).attr('method') || 'POST', // form method
            data: $(this).serialize(), // form data
            success: function (data) {
                console.log("Success");
            },
            error: function (jXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        }).done(function() {
            initChat();
        });
    });
});
	/*****************/
	/*** USER CHAT ***/
	/*****************/


function $postMessage() {
    $("#message").find("br").remove();
    let $message = $("#message").html().trim();
    $message = $message.replace(/<div>/, "<br>").replace(/<div>/g, "").replace(/<\/div>/g, "<br>").replace(/<br>/g, " ").trim();
    if ($message) {
        addMessage('user', $message);
        getResponse(0);
    }
    $("#message").empty();
}

	// Chat input
	/*Đây là sự kiện gắn với ô nhập tin nhắn có id là "message". SỰ kiện này được kích
	hoạt khi một phím được nhấn trên bàn phím khi ô nhập đang được focus
	*/
	$("#message").on("keyup", (event) => {
		if (event.which === 13) $postMessage();
	}).on("focus", () => {
		$("#message").addClass("focus");
	}).on("blur", () => {
		$("#message").removeClass("focus");
	});
	$("#send").on("click", $postMessage);

	//Show time in message
	function timeStamp() {
		const timestamp = new Date();
		const hours = timestamp.getHours();
		let minutes = timestamp.getMinutes();
		if (minutes < 10) minutes = "0" + minutes;
		const html = `<span class="timestamp">${hours}:${minutes}</span>`;
		return html;
	}

	/***************/
	/*** CHAT UI ***/
	/***************/


	// Back arrow button
	$("#back-button").on("click", () => {
		$("#landing").show();
	});

	// Menu - navigation
	$("#nav-icon").on("click", () => {
		$("#nav-container").show();
	});

	$("#nav-container").on("mouseleave", () => {
		$("#nav-container").hide();
	});

	$(".nav-link").on("click", () => {
		$("#nav-container").slideToggle(200);
	});

	// Clear history
	$("#clear-history").on("click", () => {
		$("#message-board").empty();
		$("#message").empty();
	});

	// Sign out
	$("#sign-out").on("click", () => {
		$("#message-board").empty();
		$("#message").empty();
		$("#landing").show();
		$("#username").val("");
		$("#start-chat").html("Start chat");
	});




	/*********************/
	/*** SCROLL TO END ***/
	/*********************/


	function $scrollDown() {
		const $container = $("#message-board");//Lấy ra phần tử "message-board"
		const $maxHeight = $container.height();//Lấy chiều cao tối đa của khu vực hiển thị tin nhắn
		const $scrollHeight = $container[0].scrollHeight;//Lấy chiều cao của toàn bộ nội dung
		if ($scrollHeight > $maxHeight) $container.scrollTop($scrollHeight);/*Kiểm tra nếu nội dung vượt quá thì
		hàm $container.scrollTop được gọi để cuộn xuống dưới cùng của khu vực hiển thị tin nhắn
		*/
	}




	/***************/
	/*** EMOIJIS ***/
	/***************/


	// toggle emoijis
	$("#emoi").on("click", () => {
		$("#emoijis").slideToggle(300);
		$("#emoi").toggleClass("fa fa-grin far fa-chevron-down");
	});

	// add emoiji to message
	$(".smiley").on("click", (event) => {
		const $smiley = $(event.currentTarget).clone().contents().addClass("fa-lg");
		$("#message").append($smiley);
		$("#message").select(); // ==> BUG: message field not selected after adding smiley !!
	});
});
