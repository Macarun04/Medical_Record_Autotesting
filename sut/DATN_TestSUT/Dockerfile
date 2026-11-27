FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

RUN dotnet tool install --global dotnet-coverage

COPY ["DATN_TestSUT.csproj", "./"]
RUN dotnet restore "DATN_TestSUT.csproj"

COPY . .
RUN dotnet publish "DATN_TestSUT.csproj" -c Release -o /app/publish -p:DebugType=portable -p:DebugSymbols=true

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
COPY --from=build /root/.dotnet/tools /tools
RUN mkdir -p /coverage

EXPOSE 7053
ENTRYPOINT ["dotnet", "DATN_TestSUT.dll"]