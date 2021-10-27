<?php

require_once __DIR__ . '/vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitClient
{
    private $host;
    private $port;
    private $user;
    private $pass;

    function __construct(string $host, int $port, string $user, string $pass)
    {
        $this->host = $host;
        $this->port = $port;
        $this->user = $pass;
        $this->port = $port;
    }

    private function openConnection()
    {
        return new AMQPStreamConnection($this->host, $this->port, $this->user, $this->pass);
    }

    public function login(string $username, string $password)
    {
        $connection = $this->openConnection();
        $channel = $connection->channel();

        $channel->close();
        $connection->close();
    }

    public function publish_log(string $logMsg)
    {
        $connection = $this->openConnection();
        $channel = $connection->channel();

        $channel->exchange_declare('logs', 'fanout');
        $msg = new AMQPMessage($logMsg);
        $channel->basic_publish($msg, '', 'logs');

        $channel->close();
        $connection->close();
    }
}
