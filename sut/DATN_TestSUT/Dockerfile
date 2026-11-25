FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY ["DATN_TestSUT.csproj", "./"]
RUN dotnet restore "DATN_TestSUT.csproj"

COPY . .
RUN dotnet publish "DATN_TestSUT.csproj" -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 7053
ENTRYPOINT ["dotnet", "DATN_TestSUT.dll"]