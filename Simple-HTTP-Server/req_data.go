package main

import (
	"net/http"
	"net/url"
	"time"
)

// Record struct holds request details
type Record struct {
	RemoteAddr   string      `json:"remoteaddr"`
	Method       string      `json:"method"`
	RequestURI   string      `json:"requesturi"`
	Headers      http.Header `json:"headers"`
	UserAgent    string      `json:"useragent"`
	PostForm     url.Values  `json:"postform"`
	EventTime    uint64      `json:"eventtime"`
	HoneypotName string      `json:"honeypotname"`
}

// GenerateRecord extracts request data
func GenerateRecord(r *http.Request) Record {
	data := Record{
		RemoteAddr: r.RemoteAddr,
		Method:     r.Method,
		RequestURI: r.RequestURI,
		Headers:    r.Header,
		UserAgent:  r.UserAgent(),
		EventTime:  uint64(time.Now().Unix()),
	}

	r.ParseForm()
	data.PostForm = r.PostForm

	return data
}
