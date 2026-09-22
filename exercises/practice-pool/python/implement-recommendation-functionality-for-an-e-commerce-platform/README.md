# Implement recommendation functionality for an e-commerce platform

## Problem Statement

You are building an e-commerce platform. As a part of this system, you need to expose a functionality using which the user can get recommendations for the products based on the product which the user wants to order.

## Requirements
   * product id of the product which the user wants to order
   * product_group_id of the product group to which the product belongs
   * Request will ask for recommendations for the user based on the product_id


## Instructions
1. Carefully look at `GenerateRecommendationsRequestDto` and `GenerateRecommendationsResponseDto` classes. These classes represent the request and response of the functionality which we want to implement.
2. Carefully examine the models package to understand the database schema.
3. Implement the `generate_recommendations` method inside the `RecommendationsController`.
4. Implement the `RecommendationsService` interface and fix the repository interfaces.
5. You might also need to handle cardinality between the models.
6. We will be using H2 database which is an in-memory SQL database. You do not need to implement any database related code. You just need to use the repository interfaces to interact with the database.
7. Implement the necessary exceptions in the `exceptions` package.
8. Do not modify the `RecommendationsService` interface's placeOrder method signature. You can add additional methods to the interface if you want.