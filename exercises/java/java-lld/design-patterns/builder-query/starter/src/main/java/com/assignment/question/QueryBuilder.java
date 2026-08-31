package com.assignment.question;

// TODO: implement the Builder pattern — the nested static Builder class holds a
// QueryBuilder instance it fills in via chained select/from/where/join/orderBy/groupBy
// methods (each returning `this`); build() should return a NEW QueryBuilder with all
// six fields copied from the one the Builder accumulated (not the same instance the
// fluent methods mutated), so a Builder can be reused for a second build().
@WithBuilder
public class QueryBuilder {
    private String select;
    private String from;
    private String where;
    private String join;
    private String orderBy;
    private String groupBy;

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {

        private QueryBuilder queryBuilder;

        public Builder() {
            queryBuilder = new QueryBuilder();
        }

        public Builder select(String select) {
            return this;
        }

        public Builder from(String from) {
            return this;
        }

        public Builder where(String where) {
            return this;
        }

        public Builder join(String join) {
            return this;
        }

        public Builder orderBy(String orderBy) {
            return this;
        }

        public Builder groupBy(String groupBy) {
            return this;
        }

        public QueryBuilder build() {
            return null;
        }

    }
}
