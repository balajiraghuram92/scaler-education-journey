FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8080


FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /src

COPY ["api/StudyTracker.Api.csproj", "api/"]

RUN dotnet restore "api/StudyTracker.Api.csproj"

COPY api/ api/

RUN dotnet publish "api/StudyTracker.Api.csproj" \
    -c Release \
    -o /app/publish \
    /p:UseAppHost=false


FROM base AS final

WORKDIR /app

COPY --from=build /app/publish .
COPY exercises /app/exercises

ENTRYPOINT ["dotnet", "StudyTracker.Api.dll"]
