package com.example.bmsbookticket.controllers;

import com.example.bmsbookticket.dtos.BookTicketRequestDTO;
import com.example.bmsbookticket.dtos.BookTicketResponseDTO;
import com.example.bmsbookticket.dtos.ResponseStatus;
import com.example.bmsbookticket.exceptions.SeatsUnavailableException;
import com.example.bmsbookticket.models.*;
import com.example.bmsbookticket.repositories.*;
import com.example.bmsbookticket.services.TicketService;
import com.example.bmsbookticket.services.TicketServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

// Tests 1-6 are ported from the Scaler BookMyShow "book ticket" exercise (Spring Boot + JPA + H2):
// Spring wiring is replaced by constructor wiring over in-memory repositories, assertions unchanged.
// testBookTicket_ReportsUnavailableSeatIds and testBookTicket_ConcurrentRequests_OnlyOneSucceeds
// were added for this platform (requirements 4 and 6 of the original problem statement).
public class TestTicketController {

    private TicketController ticketController;
    private TicketService ticketService;
    private ShowSeatRepository showSeatRepository;
    private UserRepository userRepository;
    private TicketRepository ticketRepository;
    private ShowRepository showRepository;
    private SeatsRepository seatRepository;

    private User user;
    private Show show;
    private List<ShowSeat> showSeats;

    @BeforeEach
    public void insertDummyData() {
        showSeatRepository = new InMemoryShowSeatRepository();
        userRepository = new InMemoryUserRepository();
        ticketRepository = new InMemoryTicketRepository();
        showRepository = new InMemoryShowRepository();
        seatRepository = new InMemorySeatsRepository();
        ticketService = new TicketServiceImpl(showSeatRepository, ticketRepository, userRepository);
        ticketController = new TicketController(ticketService);

        User u = new User();
        u.setName("Test User");
        u.setEmail("test@scaler.com");
        user = userRepository.save(u);

        Movie movie = new Movie();
        movie.setId(1);
        movie.setName("Test Movie");
        movie.setDescription("Test Description");

        show = new Show();
        show.setMovie(movie);
        show.setStartTime(new Date());
        show.setEndTime(new Date());
        show = showRepository.save(show);

        Seat seat1 = createSeat("1A", SeatType.GOLD);
        Seat seat2 = createSeat("1B", SeatType.GOLD);
        Seat seat3 = createSeat("2A", SeatType.SILVER);
        Seat seat4 = createSeat("2B", SeatType.SILVER);

        showSeats = List.of(
                createShowSeat(new ShowSeat(), seat1),
                createShowSeat(new ShowSeat(), seat2),
                createShowSeat(new ShowSeat(), seat3),
                createShowSeat(new ShowSeat(), seat4));
    }

    private Seat createSeat(String name, SeatType seatType) {
        Seat seat = new Seat();
        seat.setName(name);
        seat.setSeatType(seatType);
        return seatRepository.save(seat);
    }

    private ShowSeat createShowSeat(ShowSeat showSeat, Seat seat) {
        showSeat.setSeat(seat);
        showSeat.setShow(show);
        showSeat.setStatus(SeatStatus.AVAILABLE);
        return showSeatRepository.save(showSeat);
    }

    @Test
    public void testBookTicket_1_Request_Success() throws Exception {
        BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO.setUserId(user.getId());
        BookTicketResponseDTO responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.SUCCESS, responseDTO.getStatus(), "Status should be SUCCESS");
        assertNotNull(responseDTO.getTicket(), "Ticket should not be null");
        assertNotNull(responseDTO.getTicket().getSeats(), "Seats should not be null");
        assertEquals(2, responseDTO.getTicket().getSeats().size(), "Seats should be 2");
        assertEquals(TicketStatus.UNPAID, responseDTO.getTicket().getStatus(), "A new ticket should be UNPAID");

        Ticket ticket = responseDTO.getTicket();
        int ticketId = ticket.getId();
        ticketRepository.findById(ticketId).orElseThrow(() -> new Exception("Ticket should be stored in database"));
        List<ShowSeat> showSeats = showSeatRepository.findAll();
        assertEquals(SeatStatus.BLOCKED, showSeats.get(0).getStatus(), "Seat status should be BLOCKED");
        assertEquals(SeatStatus.BLOCKED, showSeats.get(1).getStatus(), "Seat status should be BLOCKED");
        assertEquals(SeatStatus.AVAILABLE, showSeats.get(2).getStatus(), "Seat status should be AVAILABLE");
        assertEquals(SeatStatus.AVAILABLE, showSeats.get(3).getStatus(), "Seat status should be AVAILABLE");
    }

    @Test
    public void testBookTicket_2_Request_Success_Non_overlapping_seats() throws Exception {
        BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO.setUserId(user.getId());
        BookTicketResponseDTO responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.SUCCESS, responseDTO.getStatus(), "Status should be SUCCESS");
        assertNotNull(responseDTO.getTicket(), "Ticket should not be null");
        assertNotNull(responseDTO.getTicket().getSeats(), "Seats should not be null");
        assertEquals(2, responseDTO.getTicket().getSeats().size(), "Seats should be 2");

        Ticket ticket = responseDTO.getTicket();
        int ticketId = ticket.getId();
        ticketRepository.findById(ticketId).orElseThrow(() -> new Exception("Ticket should be stored in database"));

        requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(2).getId(), showSeats.get(3).getId()));
        requestDTO.setUserId(user.getId());
        responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.SUCCESS, responseDTO.getStatus(), "Status should be SUCCESS");
        ticket = responseDTO.getTicket();
        assertNotNull(ticket, "Ticket should not be null");
        ticketId = ticket.getId();
        ticketRepository.findById(ticketId).orElseThrow(() -> new Exception("Ticket should be stored in database"));

        List<ShowSeat> showSeats = showSeatRepository.findAll();
        assertEquals(SeatStatus.BLOCKED, showSeats.get(0).getStatus(), "Seat status should be BLOCKED");
        assertEquals(SeatStatus.BLOCKED, showSeats.get(1).getStatus(), "Seat status should be BLOCKED");
        assertEquals(SeatStatus.BLOCKED, showSeats.get(2).getStatus(), "Seat status should be BLOCKED");
        assertEquals(SeatStatus.BLOCKED, showSeats.get(3).getStatus(), "Seat status should be BLOCKED");
    }

    @Test
    public void testBookTicket_NonExistingUser_Failure() {
        BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO.setUserId(100);
        BookTicketResponseDTO responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.FAILURE, responseDTO.getStatus(), "Status should be FAILURE");
        assertNull(responseDTO.getTicket(), "Ticket should be null");
        assertEquals(SeatStatus.AVAILABLE, showSeats.get(0).getStatus(), "Seat should stay AVAILABLE");
    }

    @Test
    public void testBookTicket_InvalidShowSeat_Failure() {
        BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), 100));
        requestDTO.setUserId(user.getId());
        BookTicketResponseDTO responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.FAILURE, responseDTO.getStatus(), "Status should be FAILURE");
        assertNull(responseDTO.getTicket(), "Ticket should be null");
        assertEquals(SeatStatus.AVAILABLE, showSeats.get(0).getStatus(), "Valid seat in a rejected request should stay AVAILABLE");
    }

    @Test
    public void testBookTicket_BookABookedTicket_Failure() throws Exception {
        BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO.setUserId(user.getId());
        BookTicketResponseDTO responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.SUCCESS, responseDTO.getStatus(), "Status should be SUCCESS");
        assertNotNull(responseDTO.getTicket(), "Ticket should not be null");
        assertNotNull(responseDTO.getTicket().getSeats(), "Seats should not be null");
        assertEquals(2, responseDTO.getTicket().getSeats().size(), "Seats should be 2");

        Ticket ticket = responseDTO.getTicket();
        int ticketId = ticket.getId();
        ticketRepository.findById(ticketId).orElseThrow(() -> new Exception("Ticket should be stored in database"));

        requestDTO = new BookTicketRequestDTO();
        requestDTO.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO.setUserId(user.getId());
        responseDTO = ticketController.bookTicket(requestDTO);
        assertEquals(ResponseStatus.FAILURE, responseDTO.getStatus(), "Status should be FAILURE");
        assertNull(responseDTO.getTicket(), "Ticket should be null");
    }

    @Test
    public void testBookTicket_PartiallyAvailableSeats_Failure() throws Exception {
        // First user books Seat 0 and Seat 1
        BookTicketRequestDTO requestDTO1 = new BookTicketRequestDTO();
        requestDTO1.setShowSeatIds(List.of(showSeats.get(0).getId(), showSeats.get(1).getId()));
        requestDTO1.setUserId(user.getId());
        BookTicketResponseDTO responseDTO1 = ticketController.bookTicket(requestDTO1);
        assertEquals(ResponseStatus.SUCCESS, responseDTO1.getStatus(), "First booking should succeed");

        // Second user tries to book Seat 1 (already blocked) and Seat 2 (currently available)
        BookTicketRequestDTO requestDTO2 = new BookTicketRequestDTO();
        requestDTO2.setShowSeatIds(List.of(showSeats.get(1).getId(), showSeats.get(2).getId()));
        requestDTO2.setUserId(user.getId());
        BookTicketResponseDTO responseDTO2 = ticketController.bookTicket(requestDTO2);

        // Must fail because Seat 1 is unavailable
        assertEquals(ResponseStatus.FAILURE, responseDTO2.getStatus(), "Booking should fail when any seat is unavailable");
        assertNull(responseDTO2.getTicket(), "Ticket should be null on failure");

        // Verify Seat 2 remains AVAILABLE (atomic rollback, no partial booking)
        ShowSeat seat2 = showSeatRepository.findById(showSeats.get(2).getId()).orElseThrow();
        assertEquals(SeatStatus.AVAILABLE, seat2.getStatus(), "Seat 2 should remain AVAILABLE after failed booking");
    }

    @Test
    public void testBookTicket_ReportsUnavailableSeatIds() throws Exception {
        ticketService.bookTicket(List.of(showSeats.get(0).getId()), user.getId());

        SeatsUnavailableException exception = assertThrows(SeatsUnavailableException.class,
                () -> ticketService.bookTicket(List.of(showSeats.get(0).getId(), showSeats.get(3).getId()), user.getId()),
                "Requesting a blocked seat should throw SeatsUnavailableException");
        assertEquals(List.of(showSeats.get(0).getId()), exception.getUnavailableShowSeatIds(),
                "The exception should name exactly the seats that were not available");
        assertEquals(SeatStatus.AVAILABLE, showSeats.get(3).getStatus(), "The available seat must not be blocked");
    }

    @Test
    public void testBookTicket_ConcurrentRequests_OnlyOneSucceeds() throws Exception {
        // Fresh show whose seats report their status slowly. A check-then-act implementation
        // without mutual exclusion lets every thread read AVAILABLE before any thread writes BLOCKED.
        show = showRepository.save(new Show());
        List<Integer> contestedIds = new ArrayList<>();
        for (Seat seat : List.of(createSeat("9A", SeatType.PLATINUM), createSeat("9B", SeatType.PLATINUM))) {
            contestedIds.add(createShowSeat(new SlowStatusShowSeat(), seat).getId());
        }

        int threads = 8;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        CountDownLatch startGate = new CountDownLatch(1);
        List<Future<BookTicketResponseDTO>> results = new ArrayList<>();
        for (int i = 0; i < threads; i++) {
            results.add(executor.submit(() -> {
                startGate.await();
                BookTicketRequestDTO requestDTO = new BookTicketRequestDTO();
                requestDTO.setShowSeatIds(contestedIds);
                requestDTO.setUserId(user.getId());
                return ticketController.bookTicket(requestDTO);
            }));
        }
        startGate.countDown();

        int successes = 0;
        for (Future<BookTicketResponseDTO> result : results) {
            if (result.get(30, TimeUnit.SECONDS).getStatus() == ResponseStatus.SUCCESS) {
                successes++;
            }
        }
        executor.shutdown();

        assertEquals(1, successes, "Exactly one of the concurrent requests for the same seats may succeed");
        long ticketsForContestedSeats = ticketRepository.findAll().stream()
                .filter(ticket -> ticket.getShow() != null && ticket.getShow().getId() == show.getId())
                .count();
        assertEquals(1, ticketsForContestedSeats, "Exactly one ticket should exist for the contested seats");
    }

    private static class SlowStatusShowSeat extends ShowSeat {
        @Override
        public SeatStatus getStatus() {
            SeatStatus status = super.getStatus();
            try {
                Thread.sleep(25);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return status;
        }
    }
}
