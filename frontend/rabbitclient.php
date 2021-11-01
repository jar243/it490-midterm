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
        $this->user = $user;
        $this->pass = $pass;
    }

    private function open_connection()
    {
        return new AMQPStreamConnection($this->host, $this->port, $this->user, $this->pass);
    }

    private function publish(string $route, array $args)
    {
        $connection = $this->open_connection();
        $channel = $connection->channel();
        $channel->queue_declare($route);

        $json_body = json_encode($args);
        $msg = new AMQPMessage($json_body);

        $channel->basic_publish($msg, '', $route);
    }

    private function publish_with_res(string $route, array $args)
    {
        $RES_QUEUE = 'amq.rabbitmq.reply-to';

        $connection = $this->open_connection();
        $channel = $connection->channel();

        $response = null;
        $channel->basic_consume(
            $RES_QUEUE,
            '',
            false,
            true,
            false,
            false,
            function (AMQPMessage $message) use (&$response) {
                $response = json_decode($message->body);
            },
        );

        $json_body = json_encode($args);

        $msg = new AMQPMessage(
            $json_body,
            [
                'reply_to' => $RES_QUEUE
            ],
        );

        $channel->basic_publish($msg, '', $route);
        while (is_null($response)) {
            $channel->wait();
        }

        $channel->close();
        $connection->close();

        return $response;
    }

    public function login(string $username, string $password)
    {
    }

    public function log(string $log_msg)
    {
        $connection = $this->open_connection();
        $channel = $connection->channel();

        $channel->exchange_declare('logs', 'fanout');
        $body = [
            'sender' => 'frontend-php',
            'time' => date('Y/m/d H:i:s'),
            'msg' => $log_msg,
        ];
        $json_body = json_encode($body);
        $msg = new AMQPMessage($json_body);
        $channel->basic_publish($msg, 'logs');

        $channel->close();
        $connection->close();
    }
}
