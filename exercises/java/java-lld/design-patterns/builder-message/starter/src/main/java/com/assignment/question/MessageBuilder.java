package com.assignment.question;

// TODO: implement the Builder pattern — the nested static Builder class holds a
// MessageBuilder instance it fills in via chained messageType/content/sender/recipient/
// isDelivered/timestamp methods (each returning `this`); build() should return a NEW
// MessageBuilder with all six fields copied from the one the Builder accumulated (not
// the same instance the fluent methods mutated), so a Builder can be reused for a
// second build().
@WithBuilder
public class MessageBuilder {

    private MessageType messageType;
    private String content;
    private String sender;
    private String recipient;
    private boolean isDelivered;
    private long timestamp;

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {

        private MessageBuilder messageBuilder;

        public Builder() {
            messageBuilder = new MessageBuilder();
        }

        public Builder messageType(MessageType messageType) {
            return this;
        }

        public Builder content(String content) {
            return this;
        }

        public Builder sender(String sender) {
            return this;
        }

        public Builder recipient(String recipient) {
            return this;
        }

        public Builder isDelivered(boolean isDelivered) {
            return this;
        }

        public Builder timestamp(long timestamp) {
            return this;
        }

        public MessageBuilder build() {
            return null;
        }
    }

}
