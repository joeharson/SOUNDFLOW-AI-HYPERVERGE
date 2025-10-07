import React, { useState } from 'react';
import './AudioFileUpload.css';

const AudioFileUpload = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [transcription, setTranscription] = useState(null);
    const [error, setError] = useState(null);
    const [speakerColors, setSpeakerColors] = useState({});

    // Function to generate a purple gradient
    const generatePurpleGradient = () => {
        const shades = [
            '#8e44ad', // Purple
            '#9b59b6', // Light purple
            '#6a1b9a', // Dark purple
            '#7e57c2', // Lavender purple
            '#ab47bc', // Medium purple
        ];

        const randomIndex = Math.floor(Math.random() * shades.length);
        const startColor = shades[randomIndex];
        const endColor = shades[(randomIndex + 1) % shades.length];

        return `linear-gradient(45deg, ${startColor}, ${endColor})`;
    };

    // Function to handle file upload and process audio
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Check file type
        if (!file.type.startsWith('audio/')) {
            setError('Please upload an audio file');
            return;
        }

        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('audio', file);

        try {
            const response = await fetch('http://localhost:5000/process-audio', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                setTranscription(data);
                assignColorsToSpeakers(data.segments);
            }
        } catch (err) {
            setError('Error processing audio file');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    // Function to assign colors to speakers
    const assignColorsToSpeakers = (segments) => {
        const newSpeakerColors = {};
        segments.forEach((segment) => {
            if (!newSpeakerColors[segment.speaker]) {
                newSpeakerColors[segment.speaker] = generatePurpleGradient();
            }
        });
        setSpeakerColors(newSpeakerColors);
    };

    return (
        <div className="audio-upload-container">
            <div className="upload-section">
                <label htmlFor="audio-file" className="file-upload-label">
                    <span>Upload Audio File</span>
                    <input
                        type="file"
                        id="audio-file"
                        accept="audio/*"
                        onChange={handleFileUpload}
                        className="file-input"
                    />
                </label>
            </div>

            {isLoading && <div className="loading">Processing audio...</div>}
            
            {error && <div className="error">{error}</div>}
            
            {transcription && (
                <div className="transcription-result">
                    <h3>Transcription:</h3>
                    {transcription.segments.map((segment, index) => {
                        const speakerColor = speakerColors[segment.speaker];
                        return (
                            <div key={index} className="message-bubble" style={{ background: speakerColor }}>
                                <div className="message-header">
                                    <span className="speaker" style={{ color: speakerColor }}>
                                        Speaker {segment.speaker}
                                    </span>
                                    <span className="timestamp">
                                        [{segment.start}s - {segment.end}s]
                                    </span>
                                </div>
                                <div className="text">{segment.text}</div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default AudioFileUpload;
