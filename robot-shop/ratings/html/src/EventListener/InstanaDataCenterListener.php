<?php

namespace Instana\RobotShop\Ratings\EventListener;

use Psr\Log\LoggerInterface;

class InstanaDataCenterListener
{
    private static $dataCenters = [
        "asia-northeast2",
        "asia-south1",
        "europe-west3",
        "us-east1",
        "us-west1"
    ];

    /**
     * @var LoggerInterface
     */
    private $logger;

    public function __construct(LoggerInterface $logger)
    {
        $this->logger = $logger;
    }

    public function __invoke()
    {
    }
}
