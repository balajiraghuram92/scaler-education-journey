package com.assignment.question;

// TODO: extend Publisher. updateWeatherConditions(...) should update temperature,
// humidity and pressure, then notify observers with each reading that exceeds its
// own threshold (temperature vs temperatureThreshold, humidity vs humidityThreshold,
// pressure vs pressureThreshold) — one notifyObservers(...) call per breached threshold.
public class WeatherMonitoringApplication extends Publisher {

    private double temperature;
    private double humidity;
    private double pressure;
    private double temperatureThreshold;
    private double humidityThreshold;
    private double pressureThreshold;

    // DO NOT MODIFY THIS CONSTRUCTOR
    public WeatherMonitoringApplication(double initialTemperature, double initialHumidity, double initialPressure,
                                        double temperatureThreshold, double humidityThreshold, double pressureThreshold) {
        this.temperature = initialTemperature;
        this.humidity = initialHumidity;
        this.pressure = initialPressure;
        this.temperatureThreshold = temperatureThreshold;
        this.humidityThreshold = humidityThreshold;
        this.pressureThreshold = pressureThreshold;
    }
    // DO NOT MODIFY THIS CONSTRUCTOR

    public void updateWeatherConditions(double newTemperature, double newHumidity, double newPressure) {

    }
}
