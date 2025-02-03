package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sync"
)

// Logger instance
var logger = log.New(os.Stdout, "[LOG] ", log.LstdFlags)

// Create a mutex to handle concurrent writes
var mutex sync.Mutex

// Initialize the CSV file and write headers
func init() {
	file, err := os.OpenFile("requests_log.csv", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Fatal("Unable to create or open CSV file:", err)
	}
	defer file.Close()

	// Write headers if the file is new
	fileInfo, _ := file.Stat()
	if fileInfo.Size() == 0 {
		writer := csv.NewWriter(file)
		writer.Write([]string{"RemoteAddr", "Method", "RequestURI", "UserAgent", "EventTime", "HoneypotName"})
		writer.Flush()
	}
}

// LogRecord logs request details into a CSV file
func LogRecord(r Record) error {
	mutex.Lock()
	defer mutex.Unlock()

	file, err := os.OpenFile("requests_log.csv", os.O_APPEND|os.O_WRONLY, 0666)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	record := []string{
		r.RemoteAddr,
		r.Method,
		r.RequestURI,
		r.UserAgent,
		fmt.Sprintf("%d", r.EventTime),
		r.HoneypotName,
	}

	if err := writer.Write(record); err != nil {
		return err
	}
	writer.Flush()
	logger.Println("Logged request to CSV:", record)
	return nil
}
