package main

import (
	"encoding/json"
	//"log"
	"net/http"
	"fmt"
	//"io/ioutil"
	//"strings"
	"github.com/nlopes/slack"
)



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
	allowed_tokens := map[string] bool {
		"ABCDEF" : true,
		"HIJKLM": true,
	}
	// define Slack API
	slack_api := slack.New("Slack Bot Token")
	CHANNEL_ID := "#sftp-alerts"

	var slack_attachment_color string
	//var slack_pretext string
	var slack_title string
	// If the value of Auth field in JSON POST is in the allowed_tokens map
	if allowed_tokens[json_data.Auth] {
		// Debugging: Just pring the LogMessage
		//fmt.Println(json_data.LogMessage)
		
		// Is this a success or error?
		if json_data.Action == "Success" {
			slack_attachment_color = "good"
			//slack_pretext = "SFTP Success"
			slack_title = "SFTP Success"
			fmt.Println("good")
		} else {
			slack_attachment_color = "danger"
			//slack_pretext = "SFTP Error"
			slack_title = "SFTP Error"
			fmt.Println("danger")
		}

		slack_long_message := json_data.LogMessage
		slack_attachment := slack.Attachment{
			//Pretext: slack_pretext,
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
			fmt.Printf("%s\n", err)
		} else{
			fmt.Printf("Message successfully sent to channel %s at %s", channelID, timestamp)
		}
	} else {
		fmt.Println("Invalid Auth Token")
	}


	
}

func main() {
	
	// Build HTTP server
	// Listen on root path, go to checkAuth function
	http.HandleFunc("/", checkAuth)
	// try to listen on TCP/31313 unless there's an error, then stop and display error
	if err := http.ListenAndServe(":31313", nil); err != nil {
		panic(err)
	}
}