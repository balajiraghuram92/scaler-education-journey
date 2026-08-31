package com.assignment.question;

// TODO: implement the Builder pattern — the nested static Builder class holds a
// DatabaseConfigurationBuilder instance it fills in via chained withXxx(...) methods
// (each returning `this`); build() should return a NEW DatabaseConfigurationBuilder
// with all six fields copied from the one the Builder accumulated (not the same
// instance the with-methods mutated), so a Builder can be reused for a second build().
@WithBuilder
public class DatabaseConfigurationBuilder {

    private String databaseUrl;
    private String username;
    private String password;
    private int maxConnections;
    private boolean enableCache;
    private boolean isReadOnly;

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {

        private DatabaseConfigurationBuilder databaseConfigurationBuilder;

        public Builder() {
            databaseConfigurationBuilder = new DatabaseConfigurationBuilder();
        }


        public Builder withDatabaseUrl(String databaseUrl) {
            return this;
        }

        public Builder withCredentials(String username, String password) {
            return this;
        }

        public Builder withMaxConnections(int maxConnections) {
            return this;
        }

        public Builder withEnableCache(boolean enableCache) {
            return this;
        }

        public Builder withReadOnly(boolean isReadOnly) {
            return this;
        }

        public DatabaseConfigurationBuilder build() {
            return null;
        }

    }
}
