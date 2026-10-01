package com.example.bmsbookticket.models;

import java.util.Date;
import java.util.List;

public class Ticket extends BaseModel {
    private Show show;
    private List<Seat> seats;
    private Date timeOfBooking;
    private User user;
    private TicketStatus status;

    public Show getShow() {
        return show;
    }

    public void setShow(Show show) {
        this.show = show;
    }

    public List<Seat> getSeats() {
        return seats;
    }

    public void setSeats(List<Seat> seats) {
        this.seats = seats;
    }

    public Date getTimeOfBooking() {
        return timeOfBooking;
    }

    public void setTimeOfBooking(Date timeOfBooking) {
        this.timeOfBooking = timeOfBooking;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public TicketStatus getStatus() {
        return status;
    }

    public void setStatus(TicketStatus status) {
        this.status = status;
    }
}
