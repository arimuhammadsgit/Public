package main

import (
	"fmt"
	"log"
	"net/http"
)

// handleRequest processes HTTP requests
func handleRequest(w http.ResponseWriter, req *http.Request) {
	record := GenerateRecord(req) // Generate request record

	// Log request
	if err := LogRecord(record); err != nil {
		log.Println("Error logging request:", err)
	}

	fmt.Fprintf(w, "hello\n") // Respond to client
}

func main() {
	http.HandleFunc("/", handleRequest)
	fmt.Println("Server starting on port 8080...")

	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("Error starting server:", err)
	}
}
