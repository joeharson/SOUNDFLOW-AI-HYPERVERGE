import React, { useState } from "react";
import { ReactMic } from "react-mic";
import axios from "axios";
import './AudioRecorder.css';
import AudioFileUpload from './AudioFileUpload';

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcription, setTranscription] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('record');

  const startRecording = () => {
    setRecording(true);
    setTranscription(null);
    setError(null);
  };

  const stopRecording = () => {
    setRecording(false);
  };

  const onData = (recordedBlob) => {
    console.log("Recording in progress...", recordedBlob);
  };

  const onStop = (recordedBlob) => {
    console.log("Recording stopped: ", recordedBlob);
    setAudioBlob(recordedBlob.blob);
  };

  const sendAudio = async () => {
    if (!audioBlob) {
      setError("Please record audio first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", audioBlob, "audio.wav");

    try {
      setIsLoading(true);
      setError(null);
      
      console.log("Sending request to server...");
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { 
          "Content-Type": "multipart/form-data"
        },
      });

      console.log("Server response received:", response.data);
      
      if (response.data.error) {
        throw new Error(response.data.error);
      }

      setTranscription(response.data.transcription);
    } catch (error) {
      console.error("Error details:", error);
      const errorMessage = error.response?.data?.error || error.message || "Error processing audio";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (seconds) => {
    return new Date(seconds * 1000).toISOString().substr(11, 8);
  };

  return (
    <div className="container">
      <h2>Audio Transcription Tool</h2>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'record' ? 'active' : ''}`}
          onClick={() => setActiveTab('record')}
        >
          Record Audio
        </button>
        <button 
          className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Audio
        </button>
      </div>

      {activeTab === 'record' ? (
        <div className="recorder-section">
          <h2>Audio Recorder</h2>
          <ReactMic
            record={recording}
            onStop={onStop}
            onData={onData}
            mimeType="audio/wav"
            className="sound-wave"
          />
          <div className="button-group">
            <button 
              onClick={startRecording} 
              disabled={recording || isLoading}
              className="record-button"
            >
              Start Recording
            </button>
            <button 
              onClick={stopRecording} 
              disabled={!recording || isLoading}
              className="stop-button"
            >
              Stop Recording
            </button>
            <button 
              onClick={sendAudio} 
              disabled={!audioBlob || isLoading}
              className="upload-button"
            >
              {isLoading ? "Processing..." : "Upload Audio"}
            </button>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {transcription && transcription.segments && (
            <div className="transcription-results">
              <h3>Conversation Transcript</h3>
              <div className="segments-container">
                {transcription.segments.map((segment, index) => (
                  <div 
                    key={index} 
                    className="segment"
                    data-speaker={segment.speaker || 'SPEAKER_00'}
                  >
                    <div className="segment-bubble">
                      <div className="segment-header">
                        <span className="speaker">
                          {segment.speaker === 'SPEAKER_00' ? 'Speaker A' : 'Speaker B'}
                        </span>
                        <span className="timestamp">
                          {formatTime(segment.start)}
                        </span>
                      </div>
                      <p className="segment-text">{segment.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <AudioFileUpload />
      )}
    </div>
  );
};

export default AudioRecorder;
