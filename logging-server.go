package main

import (
	"encoding/json"
	"net/http"
	//"fmt"
	"os"
	"github.com/nlopes/slack"
	"bufio"
)

func error_func(e error) {
	if e != nil {
		panic(e)
	}
}

func checkAuth(response_ http.ResponseWriter, request *http.Request) {

	// Create structure for incoming json
	type JSON_REQUEST struct {
		Auth string
		Action string
		LogMessage string
	}

	// Define JSON_ variable as the result of creating a new json decoder for the incoming request
	JSON_ := json.NewDecoder(request.Body)

	// json_data variable is of the struct type we created; it has those fields
	var json_data JSON_REQUEST

	// decode JSON_ and store it in json_data
	err := JSON_.Decode(&json_data)
	
	// if there was an error decoding the json, stop and display the error 
	if err != nil {
        panic(err)
	}
	
	// Create map of allowed auth tokens
	/* allowed_tokens := map[string] bool {
		"ABCDEF" : true,
		"HIJKLM": true,
	}*/

	// Create variable for incoming auth token
	auth_token := json_data.Auth

	// Create slice for allowed tokens
	var allowed_tokens []string

	// Open allowed tokens file
	file, err := os.Open("/path/to/allowed_tokens.txt")

	// If opening file fails, fail
	if err != nil {
		error_func(err)
	}

	// Close file
	defer file.Close()

	// Initialize file scanner
	scanner := bufio.NewScanner(file)

	// For line in file, add it to the allowed_tokens slice
	for scanner.Scan() {
		allowed_tokens = append(allowed_tokens, scanner.Text())
	}

	//
	for _, line := range allowed_tokens {
		if auth_token == line {
			slack_post(json_data.Action, json_data.LogMessage)
		} else {
			LOG_FILE := "/path/to/invalid.log"
			f, err := os.OpenFile(LOG_FILE, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0640)
			if err != nil {
				error_func(err)
			}
			_, err = f.WriteString("Invalid Auth Token: " + auth_token)
			if err != nil {
				error_func(err)
			}
		}
	}

}
	
func slack_post(action, LogMessage string) {
	// define Slack API
	slack_api := slack.New("Bot token")
	CHANNEL_ID := "#sftp-alerts"
	// Define these outside of if blocks
	var slack_attachment_color string
	var slack_title string

	if action == "Success" {
		slack_attachment_color = "good"
		slack_title = "SFTP Success"
	} else {
		slack_attachment_color = "danger"
		slack_title = "SFTP Error"
	}

	slack_long_message := LogMessage
	slack_attachment := slack.Attachment{
		Color: slack_attachment_color,
		Text: slack_long_message,
			Fields: []slack.AttachmentField{
				slack.AttachmentField{
					Title: slack_title,
				},
			},
	}
	channelID, timestamp, err := slack_api.PostMessage(CHANNEL_ID, slack.MsgOptionAttachments(slack_attachment))
	if err != nil {
		LOG_FILE := "/path/to/log.error"
		slack_fail_prefix := "Message failed to send to channel "

		f, err := os.OpenFile(LOG_FILE, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0640)
		error_func(err)

		_, err = f.WriteString(slack_fail_prefix + channelID + " " + timestamp)
		error_func(err)

	} else {
		LOG_FILE := "/path/to/log.log"
		slack_success_prefix := "Message successfully sent to channel: "

		f, err := os.OpenFile(LOG_FILE, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0640)
		error_func(err)

		defer f.Close()

		_, err = f.WriteString(slack_success_prefix + channelID + timestamp)
		error_func(err)
	} 


}

func main() {
	
	// Build HTTP server
	// Listen on root path, go to checkAuth function
	http.HandleFunc("/", checkAuth)
	
	/*
	Uncomment for HTTPS
	err := http.ListenAndServeTLS(":31313", "server.crt", "server.key", nil)
	if err != nil {
		panic(err)
	}
	*/
	// try to listen on TCP/31313 unless there's an error, then stop and display error
	if err := http.ListenAndServe(":31313", nil); err != nil {
		panic(err)
	}
}